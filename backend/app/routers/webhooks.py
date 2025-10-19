from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
import logging
import uuid
from datetime import datetime

from app.core.database import get_db
from app.models import Subscription, SubscriptionStatus, SubscriptionPlan, Payment
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
        elif event_type == "BILLING.SUBSCRIPTION.PAYMENT.FAILED":
            await handle_payment_failed(resource, db)
        elif event_type == "BILLING.SUBSCRIPTION.UPDATED":
            await handle_subscription_updated(resource, db)
        elif event_type == "PAYMENT.SALE.REFUNDED":
            await handle_payment_refunded(resource, db)
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
    """Handle subscription cancellation and downgrade to free plan."""
    subscription_id = resource.get("id")
    if not subscription_id:
        logger.error("Missing subscription ID in cancellation event")
        return
    
    subscription = db.query(Subscription).filter(
        Subscription.paypal_subscription_id == subscription_id
    ).first()
    
    if subscription:
        # Downgrade to free plan
        subscription.plan = SubscriptionPlan.FREE
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.paypal_subscription_id = None
        subscription.current_period_start = None
        subscription.current_period_end = None
        subscription.updated_at = datetime.utcnow()
        db.commit()
        logger.info(f"Subscription cancelled and downgraded to free: {subscription_id}")
    else:
        logger.warning(f"Subscription not found for PayPal ID: {subscription_id}")


async def handle_subscription_suspended(resource: dict, db: Session):
    """Handle subscription suspension and downgrade to free plan."""
    subscription_id = resource.get("id")
    if not subscription_id:
        logger.error("Missing subscription ID in suspension event")
        return
    
    subscription = db.query(Subscription).filter(
        Subscription.paypal_subscription_id == subscription_id
    ).first()
    
    if subscription:
        # Downgrade to free plan
        subscription.plan = SubscriptionPlan.FREE
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.paypal_subscription_id = None
        subscription.current_period_start = None
        subscription.current_period_end = None
        subscription.updated_at = datetime.utcnow()
        db.commit()
        logger.info(f"Subscription suspended and downgraded to free: {subscription_id}")
    else:
        logger.warning(f"Subscription not found for PayPal ID: {subscription_id}")


async def handle_subscription_expired(resource: dict, db: Session):
    """Handle subscription expiration and downgrade to free plan."""
    subscription_id = resource.get("id")
    if not subscription_id:
        logger.error("Missing subscription ID in expiration event")
        return
    
    subscription = db.query(Subscription).filter(
        Subscription.paypal_subscription_id == subscription_id
    ).first()
    
    if subscription:
        # Downgrade to free plan
        subscription.plan = SubscriptionPlan.FREE
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.paypal_subscription_id = None
        subscription.current_period_start = None
        subscription.current_period_end = None
        subscription.updated_at = datetime.utcnow()
        db.commit()
        logger.info(f"Subscription expired and downgraded to free: {subscription_id}")
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


async def handle_payment_failed(resource: dict, db: Session):
    """Handle payment failure and downgrade subscription to free plan."""
    subscription_id = resource.get("id")
    if not subscription_id:
        logger.error("Missing subscription ID in payment failed event")
        return
    
    subscription = db.query(Subscription).filter(
        Subscription.paypal_subscription_id == subscription_id
    ).first()
    
    if subscription:
        # Create a failed payment record for billing history
        # Extract amount from last_failed_payment if available
        last_failed_payment = resource.get("last_failed_payment", {})
        amount_data = last_failed_payment.get("amount", {})
        amount = float(amount_data.get("value", 0)) if amount_data.get("value") else 0.0
        currency = amount_data.get("currency_code", "USD")
        
        # Create failed payment record
        payment = Payment(
            id=str(uuid.uuid4()),
            user_id=subscription.user_id,
            subscription_id=subscription.id,
            paypal_payment_id=None,  # Failed payments may not have payment IDs
            paypal_subscription_id=subscription_id,
            amount=amount,
            currency=currency,
            status="failed",
            payment_method="paypal",
            description=f"{subscription.plan.value} subscription payment failed"
        )
        db.add(payment)
        
        # Downgrade to free plan on payment failure
        subscription.plan = SubscriptionPlan.FREE
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.paypal_subscription_id = None
        subscription.current_period_start = None
        subscription.current_period_end = None
        subscription.updated_at = datetime.utcnow()
        db.commit()
        logger.info(f"Subscription payment failed, downgraded to free: {subscription_id}, Payment record created: {payment.id}")
    else:
        logger.warning(f"Subscription not found for PayPal ID: {subscription_id}")


async def handle_subscription_updated(resource: dict, db: Session):
    """Handle subscription update (e.g., plan change)."""
    subscription_id = resource.get("id")
    if not subscription_id:
        logger.error("Missing subscription ID in update event")
        return
    
    subscription = db.query(Subscription).filter(
        Subscription.paypal_subscription_id == subscription_id
    ).first()
    
    if subscription:
        # Update billing period if available
        if "billing_info" in resource and "next_billing_time" in resource["billing_info"]:
            try:
                subscription.current_period_end = datetime.fromisoformat(
                    resource["billing_info"]["next_billing_time"].replace("Z", "+00:00")
                )
            except ValueError:
                logger.warning(f"Could not parse next_billing_time: {resource['billing_info']['next_billing_time']}")
        
        subscription.updated_at = datetime.utcnow()
        db.commit()
        logger.info(f"Subscription updated: {subscription_id}")
    else:
        logger.warning(f"Subscription not found for PayPal ID: {subscription_id}")


async def handle_payment_refunded(resource: dict, db: Session):
    """Handle payment refund."""
    payment_id = resource.get("id")
    sale_id = resource.get("sale_id")  # Original payment ID that was refunded
    
    # Find original payment by PayPal payment ID
    payment = db.query(Payment).filter(
        Payment.paypal_payment_id == sale_id
    ).first()
    
    if payment:
        # Update payment status to refunded
        payment.status = "refunded"
        payment.updated_at = datetime.utcnow()
        db.commit()
        logger.info(f"Payment refunded: {sale_id}, refund ID: {payment_id}")
    else:
        logger.warning(f"Original payment not found for refund: sale_id={sale_id}, refund_id={payment_id}")
