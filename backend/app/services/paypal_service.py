import paypalrestsdk
from typing import Optional, Dict
import logging
from datetime import datetime

from app.core.config import settings
from app.models import SubscriptionPlan

logger = logging.getLogger(__name__)


class PayPalService:
    """Service for PayPal subscription management."""
    
    def __init__(self):
        paypalrestsdk.configure({
            "mode": settings.PAYPAL_MODE,
            "client_id": settings.PAYPAL_CLIENT_ID,
            "client_secret": settings.PAYPAL_CLIENT_SECRET
        })
        
        self.plan_mapping = {
            SubscriptionPlan.BASIC_MONTHLY: settings.PAYPAL_PLAN_ID_BASIC_MONTHLY,
            SubscriptionPlan.BASIC_YEARLY: settings.PAYPAL_PLAN_ID_BASIC_YEARLY,
            SubscriptionPlan.PRO_MONTHLY: settings.PAYPAL_PLAN_ID_PRO_MONTHLY,
            SubscriptionPlan.PRO_YEARLY: settings.PAYPAL_PLAN_ID_PRO_YEARLY
        }
    
    def get_plan_id(self, plan: SubscriptionPlan) -> Optional[str]:
        """Get PayPal plan ID for a subscription tier."""
        return self.plan_mapping.get(plan)
    
    def create_subscription(
        self,
        plan: SubscriptionPlan,
        return_url: str,
        cancel_url: str,
        user_email: Optional[str] = None
    ) -> Dict:
        """Create a PayPal subscription."""
        plan_id = self.get_plan_id(plan)
        if not plan_id:
            raise ValueError(f"No PayPal plan configured for {plan}")
        
        subscription_data = {
            "plan_id": plan_id,
            "application_context": {
                "brand_name": "ProductSnap",
                "locale": "en-US",
                "shipping_preference": "NO_SHIPPING",
                "user_action": "SUBSCRIBE_NOW",
                "return_url": return_url,
                "cancel_url": cancel_url
            }
        }
        
        if user_email:
            subscription_data["subscriber"] = {
                "email_address": user_email
            }
        
        try:
            subscription = paypalrestsdk.Subscription(subscription_data)
            if subscription.create():
                logger.info(f"PayPal subscription created: {subscription.id}")
                
                # Find approval URL
                approval_url = None
                for link in subscription.links:
                    if link.rel == "approve":
                        approval_url = link.href
                        break
                
                return {
                    "subscription_id": subscription.id,
                    "status": subscription.status,
                    "approval_url": approval_url
                }
            else:
                logger.error(f"Failed to create subscription: {subscription.error}")
                raise Exception(f"PayPal error: {subscription.error}")
        except Exception as e:
            logger.error(f"PayPal subscription creation error: {e}")
            raise
    
    def get_subscription(self, subscription_id: str) -> Dict:
        """Get subscription details from PayPal."""
        try:
            subscription = paypalrestsdk.Subscription.find(subscription_id)
            return {
                "id": subscription.id,
                "status": subscription.status,
                "plan_id": subscription.plan_id,
                "start_time": subscription.start_time if hasattr(subscription, 'start_time') else None,
                "billing_info": subscription.billing_info if hasattr(subscription, 'billing_info') else None
            }
        except Exception as e:
            logger.error(f"Failed to get subscription {subscription_id}: {e}")
            raise
    
    def cancel_subscription(self, subscription_id: str, reason: str = "Customer request") -> bool:
        """Cancel a PayPal subscription."""
        try:
            subscription = paypalrestsdk.Subscription.find(subscription_id)
            if subscription.cancel({"reason": reason}):
                logger.info(f"Subscription cancelled: {subscription_id}")
                return True
            else:
                logger.error(f"Failed to cancel subscription: {subscription.error}")
                return False
        except Exception as e:
            logger.error(f"Error cancelling subscription {subscription_id}: {e}")
            return False
    
    def verify_webhook_signature(
        self,
        transmission_id: str,
        timestamp: str,
        webhook_id: str,
        event_body: str,
        cert_url: str,
        actual_signature: str,
        auth_algo: str
    ) -> bool:
        """Verify PayPal webhook signature."""
        try:
            return paypalrestsdk.WebhookEvent.verify(
                transmission_id,
                timestamp,
                webhook_id,
                event_body,
                cert_url,
                actual_signature,
                auth_algo
            )
        except Exception as e:
            logger.error(f"Webhook verification error: {e}")
            return False


paypal_service = PayPalService()
