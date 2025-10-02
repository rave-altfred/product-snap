from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class UsageCounter(Base):
    __tablename__ = "usage_counters"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    period = Column(String, nullable=False)  # Format: YYYY-MM for month, YYYY-MM-DD for day
    jobs_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Ensure unique counter per user per period
    __table_args__ = (UniqueConstraint('user_id', 'period', name='_user_period_uc'),)
    
    # Relationships
    user = relationship("User", back_populates="usage_counters")
