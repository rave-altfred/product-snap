#!/usr/bin/env python3
"""
Check PayPal Subscription Status
Usage: python scripts/check_subscription.py [subscription_id]
"""

import os
import sys
from pathlib import Path
import requests
import base64
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")
PAYPAL_MODE = os.getenv("PAYPAL_MODE", "sandbox")

if not PAYPAL_CLIENT_ID or not PAYPAL_CLIENT_SECRET:
    print("❌ Error: PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET must be set")
    sys.exit(1)

BASE_URL = "https://api-m.sandbox.paypal.com" if PAYPAL_MODE == "sandbox" else "https://api-m.paypal.com"


def get_access_token():
    """Get PayPal OAuth access token."""
    auth_url = f"{BASE_URL}/v1/oauth2/token"
    auth = base64.b64encode(f"{PAYPAL_CLIENT_ID}:{PAYPAL_CLIENT_SECRET}".encode()).decode()
    
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    
    response = requests.post(auth_url, headers=headers, data=data)
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"❌ Failed to get access token: {response.text}")
        sys.exit(1)


def check_subscription(subscription_id, access_token):
    """Check subscription details from PayPal."""
    url = f"{BASE_URL}/v1/billing/subscriptions/{subscription_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        subscription = response.json()
        
        print("=" * 70)
        print("PayPal Subscription Details")
        print("=" * 70)
        print()
        print(f"📋 Subscription ID: {subscription.get('id')}")
        print(f"📊 Status: {subscription.get('status')}")
        print(f"💳 Plan ID: {subscription.get('plan_id')}")
        print()
        
        # Subscriber info
        subscriber = subscription.get('subscriber', {})
        if subscriber:
            print("👤 Subscriber:")
            print(f"   Email: {subscriber.get('email_address', 'N/A')}")
            print()
        
        # Billing info
        billing_info = subscription.get('billing_info', {})
        if billing_info:
            print("💰 Billing Info:")
            last_payment = billing_info.get('last_payment', {})
            if last_payment:
                amount = last_payment.get('amount', {})
                print(f"   Last Payment: {amount.get('value')} {amount.get('currency_code')}")
                print(f"   Payment Time: {last_payment.get('time')}")
            
            next_billing = billing_info.get('next_billing_time')
            if next_billing:
                print(f"   Next Billing: {next_billing}")
            
            failed_count = billing_info.get('failed_payments_count', 0)
            print(f"   Failed Payments: {failed_count}")
            print()
        
        # Status transitions
        status_update_time = subscription.get('status_update_time')
        if status_update_time:
            print(f"🕐 Status Updated: {status_update_time}")
        
        create_time = subscription.get('create_time')
        if create_time:
            print(f"🕐 Created: {create_time}")
        
        start_time = subscription.get('start_time')
        if start_time:
            print(f"🕐 Started: {start_time}")
        
        print()
        print("=" * 70)
        
        # Status interpretation
        status = subscription.get('status')
        print()
        print("📝 Status Explanation:")
        if status == "APPROVAL_PENDING":
            print("   ⏳ Waiting for subscriber to approve the subscription")
        elif status == "APPROVED":
            print("   ✅ Subscription approved, waiting for first payment")
        elif status == "ACTIVE":
            print("   ✅ Subscription is active and billing")
        elif status == "SUSPENDED":
            print("   ⚠️  Subscription is suspended")
        elif status == "CANCELLED":
            print("   ❌ Subscription has been cancelled")
        elif status == "EXPIRED":
            print("   ❌ Subscription has expired")
        else:
            print(f"   ❓ Unknown status: {status}")
        
        print()
        
        return subscription
    else:
        print(f"❌ Failed to get subscription: {response.status_code}")
        print(response.text)
        return None


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/check_subscription.py <subscription_id>")
        print()
        print("Example: python scripts/check_subscription.py I-UC958BDN7W4V")
        sys.exit(1)
    
    subscription_id = sys.argv[1]
    
    print(f"🔍 Checking PayPal subscription: {subscription_id}")
    print()
    
    access_token = get_access_token()
    check_subscription(subscription_id, access_token)


if __name__ == "__main__":
    main()
