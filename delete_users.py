from sqlalchemy.orm import Session
from database import SessionLocal
from models.user import User
from models.analysis_result import AnalysisResult  # ← this is key

def delete_all_users_and_results():
    db: Session = SessionLocal()
    try:
        db.query(AnalysisResult).delete()
        db.query(User).delete()
        db.commit()
        print("✅ All analysis results and users deleted.")
    finally:
        db.close()

if __name__ == "__main__":
    delete_all_users_and_results()
