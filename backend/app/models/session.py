from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Session(Base):
    __tablename__ = "sessions"
    __table_args__ = (
        # Composite index for finding user sessions that aren't expired
        Index('ix_session_user_expires', 'user_id', 'expires_at'),
        # Index for cleanup of expired sessions
        Index('ix_session_expires', 'expires_at'),
    )
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    refresh_token_hash = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
