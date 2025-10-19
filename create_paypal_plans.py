#!/usr/bin/env python3
import requests
import json

# PayPal credentials
CLIENT_ID = "AfRGIWUrn0Ma54BwYRqe4ibpNcMFALuZiZlBmRI3ev2CORmiuDY9gTRjzZ4RGT_bBZ1W_ZE9cccayA-q"
CLIENT_SECRET = "EEKAuGJCwv4R0nxn_zhNYLPednnPsW3vuwpMnIQ3c1AxPOnzPMvPLTbtZDbMom-aSrSkl9cuXkbhuZs5"
BASE_URL = "https://api-m.sandbox.paypal.com"
PRODUCT_ID = "PROD-4RK15533F7168903V"

def get_access_token():
    """Get PayPal access token"""
    response = requests.post(
        f"{BASE_URL}/v1/oauth2/token",
        headers={
            "Accept": "application/json",
            "Accept-Language": "en_US",
        },
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={"grant_type": "client_credentials"}
    )
    return response.json()["access_token"]

def create_plan(token, name, description, price, interval_unit, interval_count=1):
    """Create a billing plan"""
    payload = {
        "product_id": PRODUCT_ID,
        "name": name,
        "description": description,
        "status": "ACTIVE",
        "billing_cycles": [
            {
                "frequency": {
                    "interval_unit": interval_unit,
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
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/v1/billing/plans",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        },
        json=payload
    )
    
    return response.json()

if __name__ == "__main__":
    print("Getting access token...")
    token = get_access_token()
    
    print("\nCreating Pro Monthly plan ($34.99)...")
    monthly_plan = create_plan(
        token,
        "Pro Monthly",
        "ProductSnap Pro - Billed Monthly at $34.99/month",
        34.99,
        "MONTH"
    )
    print(json.dumps(monthly_plan, indent=2))
    
    print("\nCreating Pro Yearly plan ($349.99)...")
    yearly_plan = create_plan(
        token,
        "Pro Yearly",
        "ProductSnap Pro - Billed Annually at $349.99/year (save 17%)",
        349.99,
        "YEAR"
    )
    print(json.dumps(yearly_plan, indent=2))
    
    if "id" in monthly_plan and "id" in yearly_plan:
        print("\n✅ Plans created successfully!")
        print(f"\nPro Monthly ID: {monthly_plan['id']}")
        print(f"Pro Yearly ID: {yearly_plan['id']}")
        print("\nUpdate your .env file with:")
        print(f"PAYPAL_PLAN_ID_PRO_MONTHLY={monthly_plan['id']}")
        print(f"PAYPAL_PLAN_ID_PRO_YEARLY={yearly_plan['id']}")
