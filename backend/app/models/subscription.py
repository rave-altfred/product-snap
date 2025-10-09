from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class SubscriptionPlan(str, enum.Enum):
    FREE = "free"
    BASIC_MONTHLY = "basic_monthly"
    BASIC_YEARLY = "basic_yearly"
    PRO_MONTHLY = "pro_monthly"
    PRO_YEARLY = "pro_yearly"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PENDING = "pending"


class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    plan = Column(Enum(SubscriptionPlan, values_callable=lambda obj: [e.value for e in obj]), default=SubscriptionPlan.FREE, nullable=False)
    status = Column(Enum(SubscriptionStatus, values_callable=lambda obj: [e.value for e in obj]), default=SubscriptionStatus.ACTIVE, nullable=False)
    paypal_subscription_id = Column(String, nullable=True, index=True)
    paypal_plan_id = Column(String, nullable=True)
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    cancel_at_period_end = Column(String, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="subscription")
