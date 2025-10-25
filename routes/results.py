from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.analysis_result import AnalysisResult
from auth import get_current_user
from models.user import User
from pydantic import BaseModel

router = APIRouter()

class RatingUpdate(BaseModel):
    rating: float

class ConfidenceUpdate(BaseModel):
    confidence: float

@router.get("/api/results")
def get_user_results(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    results = db.query(AnalysisResult).filter(AnalysisResult.user_id == current_user.id).order_by(AnalysisResult.timestamp.desc()).all()
    return [
        {
            "id": result.id,
            "filename": result.filename,
            "preview_text": result.preview_text,
            "summary_json": result.summary_json,
            "timestamp": result.timestamp,
            "user_rating": result.user_rating,
            "confidence_score": result.confidence_score
        }
        for result in results
    ]

@router.put("/api/results/{result_id}/rating")
def update_rating(
    result_id: int,
    rating_update: RatingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = db.query(AnalysisResult).filter(
        AnalysisResult.id == result_id,
        AnalysisResult.user_id == current_user.id
    ).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    if not 1 <= rating_update.rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    result.user_rating = rating_update.rating
    db.commit()
    
    return {"message": "Rating updated successfully", "rating": result.user_rating}

@router.put("/api/results/{result_id}/confidence")
def update_confidence(
    result_id: int,
    confidence_update: ConfidenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = db.query(AnalysisResult).filter(
        AnalysisResult.id == result_id,
        AnalysisResult.user_id == current_user.id
    ).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    if not 0 <= confidence_update.confidence <= 1:
        raise HTTPException(status_code=400, detail="Confidence must be between 0 and 1")
    
    result.confidence_score = confidence_update.confidence
    db.commit()
    
    return {"message": "Confidence updated successfully", "confidence": result.confidence_score}

@router.delete("/api/results/{result_id}")
def delete_result(
    result_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = db.query(AnalysisResult).filter(
        AnalysisResult.id == result_id,
        AnalysisResult.user_id == current_user.id
    ).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    db.delete(result)
    db.commit()
    
    return {"message": "Result deleted successfully"}
