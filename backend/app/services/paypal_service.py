import requests
import base64
from typing import Optional, Dict
import logging
from datetime import datetime

from app.core.config import settings
from app.models import SubscriptionPlan

logger = logging.getLogger(__name__)


class PayPalService:
    """Service for PayPal subscription management."""
    
    def __init__(self):
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.client_secret = settings.PAYPAL_CLIENT_SECRET
        self.mode = settings.PAYPAL_MODE
        
        # Set base URL based on mode
        if self.mode == "live":
            self.base_url = "https://api-m.paypal.com"
        else:
            self.base_url = "https://api-m.sandbox.paypal.com"
        
        self.plan_mapping = {
            SubscriptionPlan.BASIC_MONTHLY: settings.PAYPAL_PLAN_ID_BASIC_MONTHLY,
            SubscriptionPlan.BASIC_YEARLY: settings.PAYPAL_PLAN_ID_BASIC_YEARLY,
            SubscriptionPlan.PRO_MONTHLY: settings.PAYPAL_PLAN_ID_PRO_MONTHLY,
            SubscriptionPlan.PRO_YEARLY: settings.PAYPAL_PLAN_ID_PRO_YEARLY
        }
    
    def _get_access_token(self) -> str:
        """Get OAuth access token from PayPal."""
        auth = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials"}
        
        response = requests.post(
            f"{self.base_url}/v1/oauth2/token",
            headers=headers,
            data=data
        )
        response.raise_for_status()
        return response.json()["access_token"]
    
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
                "brand_name": "LightClick Studio",
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
            access_token = self._get_access_token()
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/v1/billing/subscriptions",
                json=subscription_data,
                headers=headers
            )
            
            if response.status_code == 201:
                result = response.json()
                logger.info(f"PayPal subscription created: {result['id']}")
                
                # Find approval URL
                approval_url = None
                for link in result.get("links", []):
                    if link.get("rel") == "approve":
                        approval_url = link.get("href")
                        break
                
                return {
                    "subscription_id": result["id"],
                    "status": result.get("status"),
                    "approval_url": approval_url
                }
            else:
                error_detail = response.json() if response.text else {"message": "Unknown error"}
                logger.error(f"Failed to create subscription: {response.status_code} - {error_detail}")
                raise Exception(f"PayPal error: {error_detail}")
        except requests.exceptions.RequestException as e:
            logger.error(f"PayPal subscription creation error: {e}")
            raise
        except Exception as e:
            logger.error(f"PayPal subscription creation error: {e}")
            raise
    
    def get_subscription(self, subscription_id: str) -> Dict:
        """Get subscription details from PayPal."""
        try:
            access_token = self._get_access_token()
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.base_url}/v1/billing/subscriptions/{subscription_id}",
                headers=headers
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                "id": result["id"],
                "status": result.get("status"),
                "plan_id": result.get("plan_id"),
                "start_time": result.get("start_time"),
                "billing_info": result.get("billing_info")
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get subscription {subscription_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to get subscription {subscription_id}: {e}")
            raise
    
    def cancel_subscription(self, subscription_id: str, reason: str = "Customer request") -> bool:
        """Cancel a PayPal subscription."""
        try:
            access_token = self._get_access_token()
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/v1/billing/subscriptions/{subscription_id}/cancel",
                json={"reason": reason},
                headers=headers
            )
            
            if response.status_code == 204:
                logger.info(f"Subscription cancelled: {subscription_id}")
                return True
            else:
                error_detail = response.json() if response.text else {"message": "Unknown error"}
                logger.error(f"Failed to cancel subscription: {response.status_code} - {error_detail}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Error cancelling subscription {subscription_id}: {e}")
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
            access_token = self._get_access_token()
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            verification_data = {
                "transmission_id": transmission_id,
                "transmission_time": timestamp,
                "cert_url": cert_url,
                "auth_algo": auth_algo,
                "transmission_sig": actual_signature,
                "webhook_id": webhook_id,
                "webhook_event": event_body
            }
            
            response = requests.post(
                f"{self.base_url}/v1/notifications/verify-webhook-signature",
                json=verification_data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("verification_status") == "SUCCESS"
            else:
                logger.error(f"Webhook verification failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Webhook verification error: {e}")
            return False


paypal_service = PayPalService()
