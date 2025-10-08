# PayPal Sandbox Quick Start

Get PayPal subscriptions up and running in 5 minutes!

## Step 1: Get PayPal Sandbox Credentials

1. Go to https://developer.paypal.com/dashboard/
2. Log in (or create a free developer account)
3. Click **Apps & Credentials**
4. Ensure **Sandbox** mode is selected
5. Click **Create App**
6. Enter app name: `ProductSnap`
7. Copy your **Client ID** and **Secret**

## Step 2: Configure Environment

Copy the example environment file:

```bash
cd /Users/ravenir/dev/apps/product-snap/backend
cp .env.example .env
```

Edit `.env` and add your PayPal credentials:

```env
PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=your_client_id_here
PAYPAL_CLIENT_SECRET=your_client_secret_here
```

## Step 3: Create Subscription Plans

Run the automated setup script:

```bash
python scripts/setup_paypal_plans.py
```

This will create 4 subscription plans in PayPal and output the Plan IDs:
- Basic Monthly ($9.99/month)
- Basic Yearly ($99.99/year)
- Pro Monthly ($29.99/month)
- Pro Yearly ($299.99/year)

Copy the Plan IDs to your `.env` file:

```env
PAYPAL_PLAN_ID_BASIC_MONTHLY=P-xxxxxxxxxxxxx
PAYPAL_PLAN_ID_BASIC_YEARLY=P-xxxxxxxxxxxxx
PAYPAL_PLAN_ID_PRO_MONTHLY=P-xxxxxxxxxxxxx
PAYPAL_PLAN_ID_PRO_YEARLY=P-xxxxxxxxxxxxx
```

## Step 4: Test It!

Start your backend:

```bash
uvicorn app.main:app --reload
```

Test the plans endpoint:

```bash
curl http://localhost:8000/api/subscriptions/plans
```

You should see all available plans including the new Basic and Pro monthly/yearly options!

## What's Next?

- **Full Setup Guide**: See `PAYPAL_SANDBOX_SETUP.md` for complete documentation
- **Webhooks**: Configure webhooks for subscription events
- **Testing**: Use PayPal sandbox accounts to test subscriptions
- **Frontend**: Update your billing page to show the 4 subscription options

## Plan Structure

| Plan | Monthly | Yearly | Features |
|------|---------|--------|----------|
| **Free** | $0 | - | 5 jobs/day, watermarked |
| **Basic** | $9.99 | $99.99 (save 17%) | 100 jobs/month, no watermarks |
| **Pro** | $29.99 | $299.99 (save 17%) | 1000 jobs/month, custom prompts, API access |

## Troubleshooting

**"Module not found" error when running setup script?**
- Install dependencies: `pip install -r requirements.txt`
- Ensure you're in the `backend` directory

**"Invalid credentials" error?**
- Double-check your Client ID and Secret in `.env`
- Ensure you're using **sandbox** credentials (not live)
- Make sure there are no extra spaces or quotes

**Plans not showing up?**
- Verify Plan IDs are correctly set in `.env`
- Restart your backend server after updating `.env`

## Support

For issues or questions:
- Check the full guide: `backend/docs/PAYPAL_SANDBOX_SETUP.md`
- PayPal Developer Docs: https://developer.paypal.com/docs/subscriptions/
- PayPal Sandbox: https://developer.paypal.com/tools/sandbox/
