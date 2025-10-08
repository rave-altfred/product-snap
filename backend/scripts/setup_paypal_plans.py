#!/usr/bin/env python3
"""
PayPal Subscription Plan Setup Script

This script automatically creates products and subscription plans in PayPal Sandbox.
It creates:
1. Basic Monthly - $9.99/month
2. Basic Yearly - $99.99/year
3. Pro Monthly - $29.99/month
4. Pro Yearly - $299.99/year

Usage:
    python scripts/setup_paypal_plans.py

Prerequisites:
    - PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET environment variables set
    - Or credentials in .env file
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
import requests
import json

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

print(f"🔧 Configuring PayPal in {PAYPAL_MODE.upper()} mode")
print(f"   Client ID: {PAYPAL_CLIENT_ID[:20]}...")
print(f"   Base URL: {BASE_URL}")
print()


def get_access_token():
    """Get PayPal OAuth access token."""
    auth_url = f"{BASE_URL}/v1/oauth2/token"
    headers = {
        "Accept": "application/json",
        "Accept-Language": "en_US"
    }
    data = {"grant_type": "client_credentials"}
    
    response = requests.post(
        auth_url,
        headers=headers,
        data=data,
        auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET)
    )
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"❌ Failed to get access token: {response.text}")
        sys.exit(1)


def create_product(access_token, name, description, category="SOFTWARE"):
    """Create a PayPal product."""
    url = f"{BASE_URL}/v1/catalogs/products"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    product_data = {
        "name": name,
        "description": description,
        "type": "SERVICE",
        "category": category
    }
    
    response = requests.post(url, headers=headers, json=product_data)
    
    if response.status_code == 201:
        product = response.json()
        print(f"✅ Created product: {name}")
        print(f"   Product ID: {product['id']}")
        return product["id"]
    else:
        print(f"❌ Failed to create product: {name}")
        print(f"   Error: {response.status_code} - {response.text}")
        return None


def create_billing_plan(access_token, product_id, plan_name, description, price, interval, interval_count=1):
    """Create a PayPal billing plan."""
    url = f"{BASE_URL}/v1/billing/plans"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    plan_data = {
        "product_id": product_id,
        "name": plan_name,
        "description": description,
        "billing_cycles": [
            {
                "frequency": {
                    "interval_unit": interval,
                    "interval_count": interval_count
                },
                "tenure_type": "REGULAR",
                "sequence": 1,
                "total_cycles": 0,
                "pricing_scheme": {
                    "fixed_price": {
                        "value": str(price),
                        "currency_code": "USD"
                    }
                }
            }
        ],
        "payment_preferences": {
            "auto_bill_outstanding": True,
            "setup_fee": {
                "value": "0",
                "currency_code": "USD"
            },
            "setup_fee_failure_action": "CONTINUE",
            "payment_failure_threshold": 3
        },
        "taxes": {
            "percentage": "0",
            "inclusive": False
        }
    }
    
    response = requests.post(url, headers=headers, json=plan_data)
    
    if response.status_code == 201:
        plan = response.json()
        print(f"✅ Created plan: {plan_name}")
        print(f"   Plan ID: {plan['id']}")
        return plan["id"]
    else:
        print(f"❌ Failed to create plan: {plan_name}")
        print(f"   Error: {response.status_code} - {response.text}")
        return None


def main():
    """Main setup function."""
    print("=" * 70)
    print("PayPal Subscription Plans Setup")
    print("=" * 70)
    print()
    
    # Get access token
    print("🔑 Getting PayPal access token...")
    access_token = get_access_token()
    print("✅ Access token obtained")
    print()
    
    # Store all plan IDs
    plan_ids = {}
    
    # Create Basic Product
    print("📦 Creating Basic Tier Product...")
    basic_product_id = create_product(
        access_token,
        "ProductSnap Basic",
        "ProductSnap Basic subscription with enhanced features and no watermarks"
    )
    
    if not basic_product_id:
        print("❌ Failed to create Basic product. Exiting.")
        sys.exit(1)
    
    print()
    
    # Create Pro Product
    print("📦 Creating Pro Tier Product...")
    pro_product_id = create_product(
        access_token,
        "ProductSnap Pro",
        "ProductSnap Pro subscription with unlimited features, custom prompts, and priority support"
    )
    
    if not pro_product_id:
        print("❌ Failed to create Pro product. Exiting.")
        sys.exit(1)
    
    print()
    print("=" * 70)
    print("Creating Subscription Plans")
    print("=" * 70)
    print()
    
    # Create Basic Monthly Plan
    print("💳 Creating Basic Monthly Plan ($9.99/month)...")
    basic_monthly_id = create_billing_plan(
        access_token,
        basic_product_id,
        "Basic Monthly",
        "ProductSnap Basic - Billed Monthly at $9.99/month",
        "9.99",
        "MONTH",
        1
    )
    if basic_monthly_id:
        plan_ids["PAYPAL_PLAN_ID_BASIC_MONTHLY"] = basic_monthly_id
    print()
    
    # Create Basic Yearly Plan
    print("💳 Creating Basic Yearly Plan ($99.99/year)...")
    basic_yearly_id = create_billing_plan(
        access_token,
        basic_product_id,
        "Basic Yearly",
        "ProductSnap Basic - Billed Annually at $99.99/year (save 17%)",
        "99.99",
        "YEAR",
        1
    )
    if basic_yearly_id:
        plan_ids["PAYPAL_PLAN_ID_BASIC_YEARLY"] = basic_yearly_id
    print()
    
    # Create Pro Monthly Plan
    print("💳 Creating Pro Monthly Plan ($39.90/month)...")
    pro_monthly_id = create_billing_plan(
        access_token,
        pro_product_id,
        "Pro Monthly",
        "ProductSnap Pro - Billed Monthly at $39.90/month",
        "39.90",
        "MONTH",
        1
    )
    if pro_monthly_id:
        plan_ids["PAYPAL_PLAN_ID_PRO_MONTHLY"] = pro_monthly_id
    print()
    
    # Create Pro Yearly Plan
    print("💳 Creating Pro Yearly Plan ($399.90/year)...")
    pro_yearly_id = create_billing_plan(
        access_token,
        pro_product_id,
        "Pro Yearly",
        "ProductSnap Pro - Billed Annually at $399.90/year (save 17%)",
        "399.90",
        "YEAR",
        1
    )
    if pro_yearly_id:
        plan_ids["PAYPAL_PLAN_ID_PRO_YEARLY"] = pro_yearly_id
    print()
    
    # Summary
    print("=" * 70)
    print("Setup Complete! 🎉")
    print("=" * 70)
    print()
    
    if len(plan_ids) == 4:
        print("✅ All 4 subscription plans created successfully!")
        print()
        print("📋 Add these to your .env file:")
        print()
        print("-" * 70)
        for key, value in plan_ids.items():
            print(f"{key}={value}")
        print("-" * 70)
        print()
        print("💡 Next steps:")
        print("   1. Copy the plan IDs above to your .env file")
        print("   2. Restart your backend server")
        print("   3. Test subscription creation via the API")
        print()
        print("📚 See backend/docs/PAYPAL_SANDBOX_SETUP.md for testing instructions")
    else:
        print(f"⚠️  Warning: Only {len(plan_ids)}/4 plans created successfully")
        print("   Review the errors above and try again")
        sys.exit(1)


if __name__ == "__main__":
    main()
