from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import logging

from app.core.database import get_db
from app.models import User, Subscription, SubscriptionPlan, SubscriptionStatus, Payment
from app.routers.auth import get_current_user
from app.services.paypal_service import paypal_service

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class CreateSubscriptionRequest(BaseModel):
    plan: str
    return_url: str = "http://localhost:3000/billing/success"
    cancel_url: str = "http://localhost:3000/billing/cancel"


class SubscriptionResponse(BaseModel):
    plan: str
    status: str
    current_period_end: Optional[str] = None
    paypal_subscription_id: Optional[str] = None


class PaymentHistoryItem(BaseModel):
    id: str
    amount: float
    currency: str
    status: str
    description: Optional[str]
    created_at: str


@router.get("/me", response_model=SubscriptionResponse)
async def get_my_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's subscription."""
    subscription = db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
    if not subscription:
        return SubscriptionResponse(
            plan="free",
            status="active",
            current_period_end=None,
            paypal_subscription_id=None
        )
    
    return SubscriptionResponse(
        plan=subscription.plan.value,
        status=subscription.status.value,
        current_period_end=subscription.current_period_end.isoformat() if subscription.current_period_end else None,
        paypal_subscription_id=subscription.paypal_subscription_id
    )


@router.get("/plans")
async def get_subscription_plans():
    """Get available subscription plans with pricing."""
    # v2.1 - Testing cache
    return {
        "plans": [
            {
                "id": "free",
                "name": "Free",
                "price": 0,
                "currency": "USD",
                "interval": "month",
                "features": [
                    "5 image generations",
                    "All three modes",
                    "Watermarked outputs"
                ]
            },
            {
                "id": "basic",
                "name": "Basic",
                "price": 9.99,
                "currency": "USD",
                "interval": "month",
                "yearly_price": 99.99,
                "yearly_savings": "Get 2 months free (Save about 17% compared to monthly)",
                "features": [
                    "100 image generations per month",
                    "All three modes",
                    "Email support"
                ]
            },
            {
                "id": "pro",
                "name": "Pro",
                "price": 34.99,
                "currency": "USD",
                "interval": "month",
                "yearly_price": 349.99,
                "yearly_savings": "Get 2 months free (Save about 17% compared to monthly)",
                "features": [
                    "500 image generations per month",
                    "All three modes",
                    "Priority queue",
                    "Priority support"
                ]
            }
        ]
    }


@router.post("/create")
async def create_subscription(
    request: CreateSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new PayPal subscription."""
    try:
        # Validate plan
        valid_plans = ["basic_monthly", "basic_yearly", "pro_monthly", "pro_yearly"]
        if request.plan not in valid_plans:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid plan. Must be one of: {', '.join(valid_plans)}"
            )
        
        # Map plan string to enum
        plan_map = {
            "basic_monthly": SubscriptionPlan.BASIC_MONTHLY,
            "basic_yearly": SubscriptionPlan.BASIC_YEARLY,
            "pro_monthly": SubscriptionPlan.PRO_MONTHLY,
            "pro_yearly": SubscriptionPlan.PRO_YEARLY
        }
        plan_enum = plan_map[request.plan]
        
        # Check if user already has any subscription (we'll update it)
        existing_subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id
        ).first()
        
        # Block if user has an active non-free subscription
        if existing_subscription and existing_subscription.status == SubscriptionStatus.ACTIVE and existing_subscription.plan != SubscriptionPlan.FREE:
            raise HTTPException(status_code=400, detail="You already have an active subscription.")
        
        # Create PayPal subscription
        paypal_response = paypal_service.create_subscription(
            plan=plan_enum,
            return_url=request.return_url,
            cancel_url=request.cancel_url,
            user_email=current_user.email
        )
        
        # Create or update subscription in database
        if existing_subscription:
            existing_subscription.plan = plan_enum
            existing_subscription.status = SubscriptionStatus.PENDING
            existing_subscription.paypal_subscription_id = paypal_response["subscription_id"]
            existing_subscription.updated_at = datetime.utcnow()
            subscription = existing_subscription
        else:
            subscription = Subscription(
                id=str(uuid.uuid4()),
                user_id=current_user.id,
                plan=plan_enum,
                status=SubscriptionStatus.PENDING,
                paypal_subscription_id=paypal_response["subscription_id"]
            )
            db.add(subscription)
        
        db.commit()
        
        return {
            "subscription_id": subscription.id,
            "paypal_subscription_id": paypal_response["subscription_id"],
            "approval_url": paypal_response["approval_url"],
            "status": "pending"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Subscription creation error: {str(e)}", exc_info=True)
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Failed to create subscription: {str(e)}")


@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel the current user's subscription."""
    try:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id,
            Subscription.status == SubscriptionStatus.ACTIVE
        ).first()
        
        if not subscription:
            raise HTTPException(status_code=404, detail="No active subscription found.")
        
        if subscription.plan == SubscriptionPlan.FREE:
            raise HTTPException(status_code=400, detail="Cannot cancel a free subscription.")
        
        if not subscription.paypal_subscription_id:
            raise HTTPException(status_code=400, detail="No PayPal subscription ID found.")
        
        # Cancel with PayPal
        success = paypal_service.cancel_subscription(
            subscription.paypal_subscription_id,
            reason="Customer requested cancellation"
        )
        
        if success:
            # Downgrade to free plan
            subscription.plan = SubscriptionPlan.FREE
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.paypal_subscription_id = None
            subscription.current_period_start = None
            subscription.current_period_end = None
            subscription.updated_at = datetime.utcnow()
            db.commit()
            
            return {
                "message": "Subscription cancelled and downgraded to free plan.",
                "subscription_id": subscription.id,
                "status": "active",
                "plan": "free"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to cancel subscription with PayPal.")
        
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Failed to cancel subscription: {str(e)}")


@router.post("/cancel-pending")
async def cancel_pending_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a pending subscription that was never completed."""
    try:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id,
            Subscription.status == SubscriptionStatus.PENDING
        ).first()
        
        if not subscription:
            raise HTTPException(status_code=404, detail="No pending subscription found.")
        
        # For pending subscriptions, just delete or reset to free
        # No need to contact PayPal since payment was never completed
        subscription.plan = SubscriptionPlan.FREE
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.paypal_subscription_id = None
        subscription.updated_at = datetime.utcnow()
        db.commit()
        
        return {
            "message": "Pending subscription cancelled successfully.",
            "subscription_id": subscription.id,
            "status": "active",
            "plan": "free"
        }
        
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Failed to cancel pending subscription: {str(e)}")


@router.get("/payments", response_model=List[PaymentHistoryItem])
async def get_payment_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payment history for current user."""
    payments = db.query(Payment).filter(
        Payment.user_id == current_user.id
    ).order_by(Payment.created_at.desc()).limit(50).all()
    
    return [
        PaymentHistoryItem(
            id=payment.id,
            amount=payment.amount,
            currency=payment.currency,
            status=payment.status,
            description=payment.description,
            created_at=payment.created_at.isoformat()
        )
        for payment in payments
    ]
