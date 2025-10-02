from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class JobMode(str, enum.Enum):
    STUDIO_WHITE = "studio_white"
    MODEL_TRYON = "model_tryon"
    LIFESTYLE_SCENE = "lifestyle_scene"


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    mode = Column(Enum(JobMode), nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False, index=True)
    
    # Input
    input_url = Column(String, nullable=False)  # S3 URL
    input_filename = Column(String, nullable=True)
    
    # Prompt
    prompt = Column(Text, nullable=True)
    prompt_override = Column(Text, nullable=True)  # For power users
    
    # Output
    result_urls = Column(JSON, default=list)  # List of S3 URLs
    thumbnail_url = Column(String, nullable=True)
    
    # Processing metadata
    nano_banana_job_id = Column(String, nullable=True, index=True)
    progress = Column(String, default=0)  # 0-100
    error_message = Column(Text, nullable=True)
    processing_time_seconds = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="jobs")
