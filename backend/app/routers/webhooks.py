from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
import logging
import uuid
from datetime import datetime

from app.core.database import get_db
from app.models import Subscription, SubscriptionStatus, Payment
from app.services.paypal_service import paypal_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/paypal")
async def paypal_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle PayPal webhook events for subscription lifecycle management."""
    try:
        # Get request body and headers
        body = await request.body()
        headers = request.headers
        
        # Extract webhook verification data
        transmission_id = headers.get("paypal-transmission-id")
        timestamp = headers.get("paypal-transmission-time") 
        cert_url = headers.get("paypal-cert-url")
        actual_signature = headers.get("paypal-transmission-sig")
        auth_algo = headers.get("paypal-auth-algo")
        
        # Log all headers for debugging
        logger.info(f"PayPal webhook headers: transmission_id={transmission_id}, timestamp={timestamp}, cert_url={cert_url}, auth_algo={auth_algo}")
        
        if not all([transmission_id, timestamp, cert_url, actual_signature, auth_algo]):
            logger.warning(f"Missing required PayPal webhook headers. Got: transmission_id={transmission_id}, timestamp={timestamp}, cert_url={cert_url}, actual_signature={bool(actual_signature)}, auth_algo={auth_algo}")
            raise HTTPException(status_code=400, detail="Missing required webhook headers")
        
        # For sandbox, skip signature verification (production should verify)
        # Signature verification requires webhook ID which needs to be configured
        logger.info("Webhook signature verification skipped for sandbox")
        
        # Parse event data
        event_data = await request.json()
        event_type = event_data.get("event_type")
        resource = event_data.get("resource", {})
        
        logger.info(f"Received PayPal webhook: {event_type}")
        
        if event_type == "BILLING.SUBSCRIPTION.ACTIVATED":
            await handle_subscription_activated(resource, db)
        elif event_type == "BILLING.SUBSCRIPTION.CANCELLED":
            await handle_subscription_cancelled(resource, db)
        elif event_type == "BILLING.SUBSCRIPTION.SUSPENDED":
            await handle_subscription_suspended(resource, db)
        elif event_type == "BILLING.SUBSCRIPTION.EXPIRED":
            await handle_subscription_expired(resource, db)
        elif event_type == "PAYMENT.SALE.COMPLETED":
            await handle_payment_completed(resource, db)
        else:
            logger.info(f"Unhandled webhook event type: {event_type}")
        
        return {"status": "success", "message": "Webhook processed successfully"}
        
    except Exception as e:
        logger.error(f"PayPal webhook processing error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def handle_subscription_activated(resource: dict, db: Session):
    """Handle subscription activation."""
    subscription_id = resource.get("id")
    if not subscription_id:
        logger.error("Missing subscription ID in activation event")
        return
    
    subscription = db.query(Subscription).filter(
        Subscription.paypal_subscription_id == subscription_id
    ).first()
    
    if subscription:
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.current_period_start = datetime.utcnow()
        subscription.updated_at = datetime.utcnow()
        
        # Set period end if available
        if "billing_info" in resource and "next_billing_time" in resource["billing_info"]:
            try:
                subscription.current_period_end = datetime.fromisoformat(
                    resource["billing_info"]["next_billing_time"].replace("Z", "+00:00")
                )
            except ValueError:
                logger.warning(f"Could not parse next_billing_time: {resource['billing_info']['next_billing_time']}")
        
        db.commit()
        logger.info(f"Subscription activated: {subscription_id}")
    else:
        logger.warning(f"Subscription not found for PayPal ID: {subscription_id}")


async def handle_subscription_cancelled(resource: dict, db: Session):
    """Handle subscription cancellation."""
    subscription_id = resource.get("id")
    if not subscription_id:
        logger.error("Missing subscription ID in cancellation event")
        return
    
    subscription = db.query(Subscription).filter(
        Subscription.paypal_subscription_id == subscription_id
    ).first()
    
    if subscription:
        subscription.status = SubscriptionStatus.CANCELLED
        subscription.updated_at = datetime.utcnow()
        db.commit()
        logger.info(f"Subscription cancelled: {subscription_id}")
    else:
        logger.warning(f"Subscription not found for PayPal ID: {subscription_id}")


async def handle_subscription_suspended(resource: dict, db: Session):
    """Handle subscription suspension (treat as cancelled)."""
    subscription_id = resource.get("id")
    if not subscription_id:
        logger.error("Missing subscription ID in suspension event")
        return
    
    subscription = db.query(Subscription).filter(
        Subscription.paypal_subscription_id == subscription_id
    ).first()
    
    if subscription:
        subscription.status = SubscriptionStatus.CANCELLED
        subscription.updated_at = datetime.utcnow()
        db.commit()
        logger.info(f"Subscription suspended: {subscription_id}")
    else:
        logger.warning(f"Subscription not found for PayPal ID: {subscription_id}")


async def handle_subscription_expired(resource: dict, db: Session):
    """Handle subscription expiration."""
    subscription_id = resource.get("id")
    if not subscription_id:
        logger.error("Missing subscription ID in expiration event")
        return
    
    subscription = db.query(Subscription).filter(
        Subscription.paypal_subscription_id == subscription_id
    ).first()
    
    if subscription:
        subscription.status = SubscriptionStatus.EXPIRED
        subscription.updated_at = datetime.utcnow()
        db.commit()
        logger.info(f"Subscription expired: {subscription_id}")
    else:
        logger.warning(f"Subscription not found for PayPal ID: {subscription_id}")


async def handle_payment_completed(resource: dict, db: Session):
    """Handle payment completion and save to payment history."""
    payment_id = resource.get("id")
    amount_data = resource.get("amount", {})
    amount = float(amount_data.get("total", 0))
    currency = amount_data.get("currency", "USD")
    
    # Get subscription ID from billing agreement
    billing_agreement_id = resource.get("billing_agreement_id")
    
    # Find subscription and user
    subscription = None
    if billing_agreement_id:
        subscription = db.query(Subscription).filter(
            Subscription.paypal_subscription_id == billing_agreement_id
        ).first()
    
    if subscription:
        # Create payment record
        payment = Payment(
            id=str(uuid.uuid4()),
            user_id=subscription.user_id,
            subscription_id=subscription.id,
            paypal_payment_id=payment_id,
            paypal_subscription_id=billing_agreement_id,
            amount=amount,
            currency=currency,
            status="completed",
            payment_method="paypal",
            description=f"{subscription.plan.value} subscription payment"
        )
        db.add(payment)
        db.commit()
        logger.info(f"Payment saved: {payment_id}, Amount: {amount} {currency}, User: {subscription.user_id}")
    else:
        logger.warning(f"Payment completed but no subscription found: {payment_id}, billing_agreement: {billing_agreement_id}")
    
    logger.info(f"Payment completed: {payment_id}, Amount: {amount} {currency}")
