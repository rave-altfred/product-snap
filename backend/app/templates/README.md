# Email Templates

This directory contains professional HTML email templates for ProductSnap with full branding integration.

## Features

✨ **Brand Colors**: Uses your ProductSnap color palette
- Primary: `#1a8fb8` (teal blue), `#154d6b` (dark blue)
- Accent: `#00d4ff` (cyan)
- Success: `#22c55e` (green)
- Gradients matching your website

🎨 **Logo Integration**: Header displays `lightclick-logo-noborder.png`
- Logo should be hosted publicly (e.g., on your frontend at `/logo.png`)
- Adjust `LOGO_URL` in `email_service.py` to point to correct URL

📱 **Responsive Design**: Works on all email clients (Gmail, Outlook, Apple Mail, etc.)
- Mobile-friendly layout
- Tables for maximum compatibility
- Inline CSS for broad support

## Available Templates

### `email_base.html`
Base template that wraps all email content with:
- Branded header with logo and gradient
- Content area (injected via `{{ content }}`)
- Professional footer with links
- Unsubscribe section

## Email Types

### 1. Verification Email
**Trigger**: User signs up
**Features**:
- Welcome message with celebration emoji 🎉
- Gradient CTA button
- Fallback link with accent color border
- 24-hour expiration notice

### 2. Password Reset Email
**Trigger**: User requests password reset
**Features**:
- Security-focused design with lock emoji 🔐
- Clear warning boxes (yellow accent)
- Primary CTA with gradient
- 1-hour expiration with security notice

### 3. Job Completion Email
**Trigger**: AI generation completes
**Features**:
- Mode-specific emojis (📸 Studio, 👔 Try-On, 🏠 Lifestyle)
- Celebratory gradient badge
- Success green CTA button
- Pro tip section with dashed border

## Customization

### Logo URL
Update in `email_service.py`:
```python
LOGO_URL = f"{settings.FRONTEND_URL}/logo.png"
```

**Important**: 
- Logo must be hosted on a public URL
- Consider using a CDN or S3 bucket for reliability
- For development, copy logo to `frontend/public/logo.png`

### Colors
All colors match your Tailwind config:
- Primary gradient: `linear-gradient(135deg, #1a8fb8 0%, #154d6b 100%)`
- Accent blue: `#00d4ff`
- Success green: `#22c55e` → `#16a34a`
- Background gradient: `#f3f4f6` → `#e0f2fe` → `#cffafe`

### Footer Links
Edit in `email_base.html`:
- Home, Pricing, Support links
- Copyright year
- Unsubscribe functionality (implement route)

## Deployment Checklist

- [ ] Host logo publicly and update `LOGO_URL`
- [ ] Verify `FRONTEND_URL` in `.env` is production URL
- [ ] Implement `/unsubscribe` route (linked in footer)
- [ ] Test emails in multiple clients (Gmail, Outlook, Apple Mail)
- [ ] Consider using email testing service (Litmus, Email on Acid)
- [ ] Set up SPF/DKIM/DMARC records for deliverability

## Testing

### Local Testing
```bash
# Send test email (requires SMTP configured)
docker-compose exec backend python -c "
from app.services.email_service import EmailService
import asyncio

async def test():
    await EmailService.send_verification_email(
        'your-email@example.com',
        'test-token-123',
        'John Doe'
    )

asyncio.run(test())
"
```

### Preview in Browser
Copy email HTML output to a file and open in browser for quick preview.

## Email Client Compatibility

✅ **Tested/Optimized for**:
- Gmail (Web, iOS, Android)
- Apple Mail (macOS, iOS)
- Outlook (2016+, Office 365, Web)
- Yahoo Mail
- Proton Mail

⚠️ **Known Limitations**:
- Outlook 2007-2013: Limited gradient support (falls back gracefully)
- Older email clients: May not render border-radius (rounded corners)
- Dark mode: Colors are optimized for light backgrounds

## Development Tips

1. **Inline CSS**: Always use inline styles for compatibility
2. **Tables for Layout**: Use `<table>` instead of `<div>` for structure
3. **Absolute Units**: Use `px` instead of `rem` or `em`
4. **Test Everything**: Email clients are notoriously inconsistent
5. **Alt Text**: Always include `alt` attributes on images
6. **Plain Text Version**: Always provide text fallback (already implemented)

## Adding New Email Types

1. Create content in `email_service.py`:
```python
@staticmethod
async def send_new_email_type(to_email: str, ...):
    content = """
    <h2 style="...">Your Title</h2>
    <p style="...">Your content</p>
    <!-- Use existing patterns from other emails -->
    """
    
    html_content = EmailService.render_template(
        "email_base.html",
        subject="Your Subject",
        content=content
    )
    
    await EmailService.send_email(to_email, "Subject", html_content, text_content)
```

2. Follow existing patterns:
- Use consistent typography (font sizes, colors)
- Include gradient CTA buttons
- Add helper sections (with colored borders)
- Include relevant emojis for engagement

## Resources

- [Email Design Best Practices](https://www.campaignmonitor.com/dev-resources/)
- [Can I Email](https://www.caniemail.com/) - CSS support checker for email clients
- [HTML Email Boilerplate](https://htmlemailboilerplate.com/)
