#!/usr/bin/env python3
"""
List PayPal Products and Plans

This script lists all products and billing plans in your PayPal account.

Usage:
    python scripts/list_paypal_plans.py
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
    sys.exit(1)

# PayPal API base URL
BASE_URL = "https://api-m.sandbox.paypal.com" if PAYPAL_MODE == "sandbox" else "https://api-m.paypal.com"


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


def list_products(access_token):
    """List all products."""
    url = f"{BASE_URL}/v1/catalogs/products"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return data.get("products", [])
    else:
        print(f"❌ Failed to list products: {response.status_code} - {response.text}")
        return []


def list_plans(access_token):
    """List all billing plans."""
    url = f"{BASE_URL}/v1/billing/plans"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return data.get("plans", [])
    else:
        print(f"❌ Failed to list plans: {response.status_code} - {response.text}")
        return []


def main():
    """Main function."""
    print("=" * 70)
    print(f"PayPal Products & Plans ({PAYPAL_MODE.upper()} Mode)")
    print("=" * 70)
    print()
    
    # Get access token
    print("🔑 Authenticating...")
    access_token = get_access_token()
    print("✅ Authenticated")
    print()
    
    # List Products
    print("=" * 70)
    print("📦 PRODUCTS")
    print("=" * 70)
    products = list_products(access_token)
    
    if products:
        for product in products:
            print(f"\n✅ {product.get('name', 'Unnamed')}")
            print(f"   ID: {product.get('id')}")
            print(f"   Description: {product.get('description', 'N/A')}")
            print(f"   Type: {product.get('type', 'N/A')}")
            print(f"   Category: {product.get('category', 'N/A')}")
    else:
        print("\nNo products found.")
    
    print()
    
    # List Plans
    print("=" * 70)
    print("💳 SUBSCRIPTION PLANS")
    print("=" * 70)
    plans = list_plans(access_token)
    
    if plans:
        for plan in plans:
            print(f"\n✅ {plan.get('name', 'Unnamed')}")
            print(f"   ID: {plan.get('id')}")
            print(f"   Description: {plan.get('description', 'N/A')}")
            print(f"   Status: {plan.get('status', 'N/A')}")
            print(f"   Product ID: {plan.get('product_id', 'N/A')}")
            
            # Show pricing if available
            if 'billing_cycles' in plan and plan['billing_cycles']:
                cycle = plan['billing_cycles'][0]
                if 'pricing_scheme' in cycle and 'fixed_price' in cycle['pricing_scheme']:
                    price = cycle['pricing_scheme']['fixed_price']
                    freq = cycle.get('frequency', {})
                    interval = freq.get('interval_unit', 'N/A')
                    print(f"   Price: ${price.get('value', 'N/A')} {price.get('currency_code', 'USD')} per {interval}")
    else:
        print("\nNo plans found.")
    
    print()
    print("=" * 70)
    print(f"View in browser: {BASE_URL.replace('api-m', 'www')}")
    print("=" * 70)


if __name__ == "__main__":
    main()
