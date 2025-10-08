# PayPal Sandbox Setup Guide

This guide walks you through setting up PayPal sandbox for ProductSnap with the following subscription plans:

## Subscription Plans

1. **Basic Monthly** - $9.99/month
2. **Basic Yearly** - $99.99/year (save ~17%)
3. **Pro Monthly** - $29.99/month
4. **Pro Yearly** - $299.99/year (save ~17%)

## Prerequisites

- PayPal Developer Account (https://developer.paypal.com)
- PayPal REST SDK installed (`pip install paypalrestsdk`)

## Step 1: Create Sandbox Business Account

1. Go to https://developer.paypal.com/dashboard/
2. Navigate to **Sandbox > Accounts**
3. Click **Create Account**
4. Select **Business** account type
5. Fill in details:
   - Email: `productsnap-business@example.com`
   - Password: (choose a secure password)
   - First Name: `ProductSnap`
   - Last Name: `Business`
5. Click **Create Account**

## Step 2: Create Sandbox Personal Account (for testing)

1. In the same **Sandbox > Accounts** section
2. Click **Create Account**
3. Select **Personal** account type
4. Fill in details:
   - Email: `productsnap-buyer@example.com`
   - Password: (choose a secure password)
5. Click **Create Account**

## Step 3: Get API Credentials

1. Navigate to **Apps & Credentials**
2. Ensure you're in **Sandbox** mode (toggle at top)
3. Click **Create App**
4. Enter App Name: `ProductSnap`
5. Select the business sandbox account you created
6. Click **Create App**
7. Copy your:
   - **Client ID**
   - **Secret** (click "Show" to reveal)

## Step 4: Create Subscription Products and Plans

You can either:

### Option A: Use the Automated Script (Recommended)

Run the provided script to automatically create all products and plans:

```bash
cd /Users/ravenir/dev/apps/product-snap/backend
python scripts/setup_paypal_plans.py
```

This script will:
1. Create products for Basic and Pro tiers
2. Create 4 subscription plans (Basic Monthly, Basic Yearly, Pro Monthly, Pro Yearly)
3. Output the Plan IDs to add to your `.env` file

### Option B: Manual Creation via PayPal Dashboard

1. Go to https://www.sandbox.paypal.com/billing/plans
2. Log in with your business sandbox account
3. For each plan:
   - Click **Create Plan**
   - Enter plan details (name, description, pricing)
   - Set billing cycle (monthly or yearly)
   - Save and copy the Plan ID

## Step 5: Update Environment Variables

Add the following to your `.env` file:

```env
# PayPal Configuration
PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=your_client_id_here
PAYPAL_CLIENT_SECRET=your_client_secret_here

# PayPal Plan IDs (from Step 4)
PAYPAL_PLAN_ID_BASIC_MONTHLY=P-XXXXXXXXXXXXXXXXXX
PAYPAL_PLAN_ID_BASIC_YEARLY=P-XXXXXXXXXXXXXXXXXX
PAYPAL_PLAN_ID_PRO_MONTHLY=P-XXXXXXXXXXXXXXXXXX
PAYPAL_PLAN_ID_PRO_YEARLY=P-XXXXXXXXXXXXXXXXXX
```

## Step 6: Set Up Webhook (Optional but Recommended)

Webhooks allow PayPal to notify your app of subscription events (activated, cancelled, payment failed, etc.)

1. In PayPal Developer Dashboard, go to your app
2. Scroll down to **Webhooks**
3. Click **Add Webhook**
4. Enter Webhook URL: `https://your-domain.com/api/webhooks/paypal`
   - For local testing, use ngrok: `https://your-ngrok-url.ngrok.io/api/webhooks/paypal`
5. Select event types:
   - `BILLING.SUBSCRIPTION.ACTIVATED`
   - `BILLING.SUBSCRIPTION.CANCELLED`
   - `BILLING.SUBSCRIPTION.EXPIRED`
   - `BILLING.SUBSCRIPTION.SUSPENDED`
   - `BILLING.SUBSCRIPTION.UPDATED`
   - `PAYMENT.SALE.COMPLETED`
   - `PAYMENT.SALE.REFUNDED`
6. Save and copy the **Webhook ID**
7. Add to `.env`:
   ```env
   PAYPAL_WEBHOOK_ID=your_webhook_id_here
   ```

## Step 7: Testing the Integration

### Test Subscription Creation

1. Start your backend server:
   ```bash
   cd /Users/ravenir/dev/apps/product-snap/backend
   uvicorn app.main:app --reload
   ```

2. Make a test API call:
   ```bash
   curl -X POST http://localhost:8000/api/subscriptions/create \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -d '{
       "plan": "basic_monthly",
       "return_url": "http://localhost:3000/billing/success",
       "cancel_url": "http://localhost:3000/billing/cancel"
     }'
   ```

3. You'll receive an `approval_url` - open it in a browser
4. Log in with your **personal sandbox account** (`productsnap-buyer@example.com`)
5. Complete the subscription approval

### Test Payment Credentials (Sandbox)

Use these test credit cards in PayPal sandbox:
- **Visa**: 4032039185387692
- **Mastercard**: 5425874392945625
- **Amex**: 374352570730338
- CVV: Any 3 digits (4 for Amex)
- Expiry: Any future date

## Plan Features

Configure these in your application logic:

### Free Plan
- 5 jobs per day
- 1 concurrent job
- Watermarked outputs
- Basic support

### Basic Plan (Monthly/Yearly)
- 100 jobs per month
- 3 concurrent jobs
- No watermarks
- Email support
- Priority queue

### Pro Plan (Monthly/Yearly)
- 1000 jobs per month
- 5 concurrent jobs
- No watermarks
- Custom prompts
- Priority support
- API access

## Troubleshooting

### "Invalid client credentials"
- Verify your Client ID and Secret are correct
- Ensure you're using **sandbox** credentials (not live)
- Check that PAYPAL_MODE is set to "sandbox"

### "Invalid plan ID"
- Verify plan IDs in `.env` match those created in PayPal
- Ensure plans are created in **sandbox** mode
- Plan IDs start with "P-"

### Webhook not receiving events
- Verify webhook URL is accessible (use ngrok for local testing)
- Check webhook ID is correct in `.env`
- Verify selected event types in PayPal dashboard

## Going to Production

When ready to go live:

1. Create a live PayPal Business account
2. Go through PayPal's verification process
3. Create production app in PayPal Developer Dashboard
4. Create production plans
5. Update `.env` with production credentials:
   ```env
   PAYPAL_MODE=live
   PAYPAL_CLIENT_ID=production_client_id
   PAYPAL_CLIENT_SECRET=production_secret
   # ... production plan IDs
   ```

## Additional Resources

- [PayPal Subscriptions API](https://developer.paypal.com/docs/subscriptions/)
- [PayPal REST SDK Python](https://github.com/paypal/PayPal-Python-SDK)
- [PayPal Sandbox Testing](https://developer.paypal.com/tools/sandbox/)
