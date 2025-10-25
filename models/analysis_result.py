from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))  # Changed to String to match User.id
    filename = Column(String(100))
    preview_text = Column(Text)
    summary_json = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_rating = Column(Float, nullable=True)  # User rating (1-5)
    confidence_score = Column(Float, nullable=True)  # AI confidence score

    user = relationship("User", back_populates="results")
