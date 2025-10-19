#!/usr/bin/env python3
"""
Setup PayPal Webhook for Subscription Events
Usage: python scripts/setup_paypal_webhook.py
"""

import os
import sys
from pathlib import Path
import requests
import base64
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")
PAYPAL_MODE = os.getenv("PAYPAL_MODE", "sandbox")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

if not PAYPAL_CLIENT_ID or not PAYPAL_CLIENT_SECRET:
    print("❌ Error: PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET must be set")
    sys.exit(1)

BASE_URL = "https://api-m.sandbox.paypal.com" if PAYPAL_MODE == "sandbox" else "https://api-m.paypal.com"

print("=" * 70)
print("PayPal Webhook Setup")
print("=" * 70)
print()
print(f"🔧 Mode: {PAYPAL_MODE.upper()}")
print(f"   Backend URL: {BACKEND_URL}")
print()


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


def list_webhooks(access_token):
    """List existing webhooks."""
    url = f"{BASE_URL}/v1/notifications/webhooks"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        webhooks = response.json().get("webhooks", [])
        return webhooks
    else:
        print(f"⚠️  Could not list webhooks: {response.status_code}")
        print(response.text)
        return []


def create_webhook(access_token, webhook_url):
    """Create a new webhook."""
    url = f"{BASE_URL}/v1/notifications/webhooks"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Subscription-related events to listen for
    event_types = [
        {"name": "BILLING.SUBSCRIPTION.ACTIVATED"},
        {"name": "BILLING.SUBSCRIPTION.CANCELLED"},
        {"name": "BILLING.SUBSCRIPTION.SUSPENDED"},
        {"name": "BILLING.SUBSCRIPTION.EXPIRED"},
        {"name": "BILLING.SUBSCRIPTION.UPDATED"},
        {"name": "BILLING.SUBSCRIPTION.PAYMENT.FAILED"},
        {"name": "PAYMENT.SALE.COMPLETED"},
        {"name": "PAYMENT.SALE.REFUNDED"}
    ]
    
    webhook_data = {
        "url": webhook_url,
        "event_types": event_types
    }
    
    response = requests.post(url, json=webhook_data, headers=headers)
    
    if response.status_code == 201:
        webhook = response.json()
        return webhook
    else:
        print(f"❌ Failed to create webhook: {response.status_code}")
        print(response.text)
        return None


def delete_webhook(access_token, webhook_id):
    """Delete a webhook."""
    url = f"{BASE_URL}/v1/notifications/webhooks/{webhook_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.delete(url, headers=headers)
    
    if response.status_code == 204:
        return True
    else:
        print(f"⚠️  Could not delete webhook {webhook_id}: {response.status_code}")
        return False


def main():
    """Main function."""
    print("🔑 Getting PayPal access token...")
    access_token = get_access_token()
    print("✅ Access token obtained")
    print()
    
    # List existing webhooks
    print("📋 Checking existing webhooks...")
    existing_webhooks = list_webhooks(access_token)
    
    if existing_webhooks:
        print(f"   Found {len(existing_webhooks)} existing webhook(s):")
        for webhook in existing_webhooks:
            print(f"   • {webhook.get('url')}")
            print(f"     ID: {webhook.get('id')}")
            print(f"     Events: {len(webhook.get('event_types', []))}")
            print()
    else:
        print("   No existing webhooks found")
        print()
    
    # Determine webhook URL
    webhook_url = f"{BACKEND_URL}/api/webhooks/paypal"
    
    print("-" * 70)
    print()
    print(f"🎯 Webhook URL: {webhook_url}")
    print()
    
    # Check if webhook already exists for this URL
    existing_webhook = None
    for webhook in existing_webhooks:
        if webhook.get('url') == webhook_url:
            existing_webhook = webhook
            break
    
    if existing_webhook:
        print("✅ Webhook already exists for this URL!")
        print(f"   Webhook ID: {existing_webhook.get('id')}")
        print()
        print("💡 To delete and recreate, run:")
        print(f"   python scripts/setup_paypal_webhook.py --delete {existing_webhook.get('id')}")
        print()
        
        # Store webhook ID in .env suggestion
        print("📝 Add this to your .env file:")
        print(f"   PAYPAL_WEBHOOK_ID={existing_webhook.get('id')}")
        print()
    else:
        print("📝 Creating new webhook...")
        
        if PAYPAL_MODE == "sandbox" and "localhost" in webhook_url:
            print()
            print("⚠️  WARNING: You're using localhost with sandbox mode!")
            print("   PayPal cannot reach localhost webhooks.")
            print()
            print("   Options:")
            print("   1. Use ngrok or similar tool to expose localhost")
            print("   2. Deploy to a public server (e.g., Digital Ocean)")
            print("   3. For testing, manually sync subscription status")
            print()
            
            response = input("   Continue anyway? (y/N): ")
            if response.lower() != 'y':
                print("   Aborted.")
                sys.exit(0)
            print()
        
        webhook = create_webhook(access_token, webhook_url)
        
        if webhook:
            print("✅ Webhook created successfully!")
            print(f"   Webhook ID: {webhook.get('id')}")
            print(f"   URL: {webhook.get('url')}")
            print(f"   Events: {len(webhook.get('event_types', []))}")
            print()
            print("📝 Add this to your .env file:")
            print(f"   PAYPAL_WEBHOOK_ID={webhook.get('id')}")
            print()
            print("🎉 Webhook setup complete!")
        else:
            print("❌ Failed to create webhook")
            sys.exit(1)
    
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
