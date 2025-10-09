#!/usr/bin/env python3
"""
List PayPal Sandbox Test Accounts
Usage: python scripts/list_sandbox_accounts.py
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

if not PAYPAL_CLIENT_ID or not PAYPAL_CLIENT_SECRET:
    print("❌ Error: PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET must be set")
    print("   Set them in your .env file or as environment variables")
    sys.exit(1)

# PayPal API base URL
BASE_URL = "https://api-m.sandbox.paypal.com" if PAYPAL_MODE == "sandbox" else "https://api-m.paypal.com"

print("=" * 70)
print("PayPal Sandbox Test Accounts")
print("=" * 70)
print()
print(f"🔧 Mode: {PAYPAL_MODE.upper()}")
print(f"   Client ID: {PAYPAL_CLIENT_ID[:20]}...")
print(f"   Base URL: {BASE_URL}")
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


def list_sandbox_accounts(access_token):
    """
    Note: PayPal's REST API doesn't have a direct endpoint to list sandbox accounts.
    This information is only available through the Developer Dashboard UI.
    
    However, we can show you where to find them and provide instructions.
    """
    print("ℹ️  PayPal Sandbox Accounts Information")
    print("-" * 70)
    print()
    print("📋 How to View Your Sandbox Test Accounts:")
    print()
    print("1. Go to: https://developer.paypal.com/dashboard/")
    print("2. Log in with your PayPal account")
    print("3. Click 'Testing Tools' → 'Sandbox Accounts' in the left menu")
    print()
    print("You should see:")
    print("  • Personal Account (buyer) - Use this to test subscriptions")
    print("  • Business Account (merchant) - Already linked to your app")
    print()
    print("-" * 70)
    print()
    
    # We can verify the API credentials work
    print("🔍 Verifying API Credentials...")
    
    # Test by getting token info
    token_info_url = f"{BASE_URL}/v1/oauth2/token/userinfo"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(token_info_url, headers=headers)
    
    if response.status_code == 200:
        print("✅ API credentials are valid!")
        print()
    else:
        print(f"⚠️  Could not verify token info: {response.status_code}")
        print()
    
    # Show created plans/products as additional info
    print("📦 Your PayPal Products & Plans:")
    print("-" * 70)
    
    # List products
    products_url = f"{BASE_URL}/v1/catalogs/products"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(products_url, headers=headers, params={"page_size": 20})
    
    if response.status_code == 200:
        products = response.json().get("products", [])
        if products:
            print("\n🏷️  Products:")
            for product in products:
                print(f"  • {product['name']}")
                print(f"    ID: {product['id']}")
                print()
        else:
            print("  No products found")
    
    # List billing plans
    plans_url = f"{BASE_URL}/v1/billing/plans"
    response = requests.get(plans_url, headers=headers, params={"page_size": 20})
    
    if response.status_code == 200:
        plans = response.json().get("plans", [])
        if plans:
            print("\n💳 Billing Plans:")
            for plan in plans:
                status = plan.get("status", "N/A")
                print(f"  • {plan['name']}")
                print(f"    ID: {plan['id']}")
                print(f"    Status: {status}")
                print()
        else:
            print("  No billing plans found")
    
    print("-" * 70)
    print()
    print("💡 To Test Subscriptions:")
    print()
    print("1. Start subscription flow in your app")
    print("2. When redirected to PayPal, use a PERSONAL test account")
    print("3. Email format: sb-xxxxx@personal.example.com")
    print("4. Get credentials from Developer Dashboard → Sandbox Accounts")
    print()
    print("🔗 Direct Link: https://developer.paypal.com/dashboard/accounts")
    print()


def main():
    """Main function."""
    print("🔑 Getting PayPal access token...")
    access_token = get_access_token()
    print("✅ Access token obtained")
    print()
    
    list_sandbox_accounts(access_token)
    
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
