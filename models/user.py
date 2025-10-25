from sqlalchemy import Column, Integer, String, Text
from database import Base
from sqlalchemy.orm import relationship
from models.analysis_result import AnalysisResult


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)  # Changed to String to support Clerk IDs
    email = Column(String, unique=True, index=True, nullable=True)  # Made nullable for Clerk users
    hashed_password = Column(String, nullable=True)  # Made nullable for Clerk users
    full_name = Column(String)
    results = relationship("AnalysisResult", back_populates="user")
