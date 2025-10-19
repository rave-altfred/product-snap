#!/usr/bin/env python3
"""
Fix stuck subscriptions by checking real status from PayPal API.
Usage: python fix_stuck_subscription.py <paypal_subscription_id>
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import SessionLocal
from app.models import Subscription, SubscriptionPlan, SubscriptionStatus
from app.services.paypal_service import paypal_service
from datetime import datetime


def fix_subscription(paypal_subscription_id: str):
    """Check PayPal API and sync subscription status."""
    db = SessionLocal()
    try:
        # Find subscription in database
        subscription = db.query(Subscription).filter(
            Subscription.paypal_subscription_id == paypal_subscription_id
        ).first()
        
        if not subscription:
            print(f"❌ Subscription not found in database: {paypal_subscription_id}")
            return
        
        print(f"📋 Current DB status: plan={subscription.plan.value}, status={subscription.status.value}")
        
        # Get real status from PayPal
        print(f"🔍 Checking PayPal API...")
        paypal_data = paypal_service.get_subscription(paypal_subscription_id)
        
        paypal_status = paypal_data.get("status", "").upper()
        print(f"📡 PayPal status: {paypal_status}")
        
        # Handle different PayPal statuses
        if paypal_status == "ACTIVE":
            print("✅ Subscription is active on PayPal")
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.updated_at = datetime.utcnow()
        elif paypal_status in ["CANCELLED", "SUSPENDED", "EXPIRED"]:
            print(f"⚠️  Subscription is {paypal_status} on PayPal, downgrading to free")
            subscription.plan = SubscriptionPlan.FREE
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.paypal_subscription_id = None
            subscription.current_period_start = None
            subscription.current_period_end = None
            subscription.updated_at = datetime.utcnow()
        elif paypal_status == "APPROVAL_PENDING":
            print("⏳ Subscription pending approval on PayPal")
            subscription.status = SubscriptionStatus.PENDING
            subscription.updated_at = datetime.utcnow()
        else:
            print(f"❓ Unknown PayPal status: {paypal_status}")
            return
        
        db.commit()
        print(f"✅ Subscription updated: plan={subscription.plan.value}, status={subscription.status.value}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fix_stuck_subscription.py <paypal_subscription_id>")
        print("Example: python fix_stuck_subscription.py I-UC958BDN7W4V")
        sys.exit(1)
    
    paypal_sub_id = sys.argv[1]
    fix_subscription(paypal_sub_id)
