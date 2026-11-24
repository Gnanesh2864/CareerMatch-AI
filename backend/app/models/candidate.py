import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    raw_resume_text = Column(Text, nullable=True)
    resume_filename = Column(String(255), nullable=True)
    structured_data_json = Column(Text, nullable=True)  # JSON representation of validated CandidateProfileSchema
    embedding_json = Column(Text, nullable=True)       # Serialized dense vector embedding
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="profile")
