from fastapi import FastAPI, File, UploadFile, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path, PurePath
from sqlalchemy.orm import Session
import os
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from jose import JWTError, jwt
import re
import boto3
import requests

from routes import auth_routes, results
from models.user import Base, User
from database import engine, SessionLocal
from auth import get_current_user
from models.analysis_result import AnalysisResult

# Database table creation
Base.metadata.create_all(bind=engine)

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("Missing OPENAI_API_KEY in environment variables.")
client = OpenAI(api_key=api_key)

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001", "http://172.29.208.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Swagger UI JWT setup
app.openapi_schema = None
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="FastAPI",
        version="0.1.0",
        description="Secure JWT-enabled API",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", []).append({"BearerAuth": []})
    app.openapi_schema = openapi_schema
    return app.openapi_schema
app.openapi = custom_openapi

# Include authentication routes
app.include_router(auth_routes.router)

# Include results routes
app.include_router(results.router)

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Health check
@app.get("/api/test")
def test_route():
    return {"message": "Python backend is working!"}

# File upload
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

def upload_file_to_s3(file_bytes, filename, content_type):
    s3_client.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=filename,
        Body=file_bytes,
        ContentType=content_type,
    )
    return f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{filename}"

@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    safe_filename = PurePath(file.filename).name
    if not safe_filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    if len(safe_filename) > 100:
        raise HTTPException(status_code=400, detail="Filename is too long.")

    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (limit 5MB)")

    # Upload to S3
    s3_url = upload_file_to_s3(contents, safe_filename, file.content_type)

    # Read PDF from bytes (not from file_location)
    from io import BytesIO
    reader = PdfReader(BytesIO(contents))
    text_pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            clean = text.strip()
            if len(clean) > 100 and not clean.lower().startswith("confidential"):
                text_pages.append(clean)
            if len(text_pages) >= 10:
                break
    text = "\n\n".join(text_pages)
    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="File uploaded but no readable business content was found in the PDF."
        )

    prompt = f"""
You are a top-tier private equity investment analyst. Extract only clear, actionable, investment-focused insights from the Confidential Information Memorandum (CIM) excerpt below. Do not hallucinate or guess beyond what's written. Return only what is explicitly stated or clearly implied.

Summarize in this JSON format (no markdown):

{{
  "COMPANY INFO": {{
    "Name": "",
    "Description": ""
  }},
  "FINANCIALS": {{
    "Actuals": {{
      "revenue": "", 
      "EBITDA": "", 
      "year": "", 
      "margin": "", 
      "FCF": ""
    }},
    "Estimates": {{
      "forward revenue": "", 
      "EBITDA": "", 
      "capex": "", 
      "capex/revenue": ""
    }}
  }},
  "THESIS": ["Key investment thesis points as bullet points"],
  "RED FLAGS": ["Key risks or concerns as bullet points"],
  "SUMMARY": "Concise, plain-English summary of the CIM excerpt.",
  "confidence_score": 0,
  "confidence_breakdown": {{
    "COMPANY INFO": 0,
    "FINANCIALS": 0,
    "THESIS": 0,
    "RED FLAGS": 0,
    "SUMMARY": 0
  }},
  "flagged_fields": [],
  "low_confidence_flags": ""
}}

If a field is missing, use "" or "unknown" (not null). Be concise and factual. Focus on what a private equity team would want to know for a quick investment meeting.

CIM EXCERPT (first 10 pages):
{text[:10000]}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an investment analyst reviewing CIMs."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
        )
        result = response.choices[0].message.content.strip()
        # Remove markdown code block formatting if present
        result = re.sub(r"^```json|^```|```$", "", result, flags=re.MULTILINE).strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI analysis failed: {str(e)}")

    # Store result in DB
    analysis = AnalysisResult(
        filename=safe_filename,
        preview_text=text[:1000],
        summary_json=result,
        user_id=current_user.id,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return {
        "filename": safe_filename,
        "message": "File uploaded and analyzed!",
        "preview_text": text[:300],
        "llm_analysis": result,
        "note": "This is a first-pass summary and investment memo by GPT-4o."
    }

# Mount static frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_frontend(request: Request):
    with open("static/frontend.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content, status_code=200)
