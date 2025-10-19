import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from typing import Optional
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import settings

logger = logging.getLogger(__name__)

# Setup Jinja2 for email templates
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(['html', 'xml'])
)


class EmailService:
    """Service for sending emails."""
    
    # Logo URL - should be hosted publicly for email clients
    LOGO_URL = f"{settings.FRONTEND_URL}/logo.png"  # Adjust based on your hosting
    
    @staticmethod
    def render_template(template_name: str, **context) -> str:
        """Render an email template with context."""
        try:
            from markupsafe import Markup
        except ImportError:
            from jinja2 import Markup
        
        # Mark HTML content as safe so Jinja2 doesn't escape it
        if 'content' in context:
            context['content'] = Markup(context['content'])
        
        template = jinja_env.get_template(template_name)
        return template.render(
            logo_url=EmailService.LOGO_URL,
            frontend_url=settings.FRONTEND_URL,
            unsubscribe_url=f"{settings.FRONTEND_URL}/unsubscribe",
            **context
        )
    
    @staticmethod
    async def send_email(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ):
        """Send an email via SMTP."""
        # Skip email sending if SMTP is not configured
        if not settings.SMTP_HOST or not settings.SMTP_USER:
            logger.warning(f"SMTP not configured, skipping email to {to_email}")
            return
        
        # Create HTML-only message (simpler, more reliable)
        message = MIMEText(html_content, "html", "utf-8")
        message["From"] = settings.SMTP_FROM
        message["Reply-To"] = settings.SMTP_FROM
        message["To"] = to_email
        message["Subject"] = subject
        
        # Explicitly set Content-Type to ensure HTML rendering
        message.replace_header("Content-Type", 'text/html; charset="utf-8"')
        
        # Debug logging
        logger.info(f"Sending email with Content-Type: {message.get('Content-Type')}")
        
        try:
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                start_tls=settings.SMTP_TLS  # Use STARTTLS instead of direct TLS
            )
            logger.info(f"Email sent to {to_email} with subject: {subject}")
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            raise
    
    @staticmethod
    async def send_verification_email(to_email: str, token: str, user_name: Optional[str] = None):
        """Send email verification link."""
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        greeting = f"Hi {user_name}," if user_name else "Hi,"
        
        content = f"""
        <h2 style="margin: 0 0 20px 0; color: #111827; font-size: 28px; font-weight: 700; line-height: 1.3;">
            Welcome to LightClick Studio! 🎉
        </h2>
        <p style="margin: 0 0 20px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
            {greeting}
        </p>
        <p style="margin: 0 0 30px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
            Thanks for signing up! We're excited to help you create amazing product photos with AI.
            To get started, please verify your email address by clicking the button below:
        </p>
        
        <!-- CTA Button -->
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="margin: 30px 0;">
            <tr>
                <td align="center">
                    <table role="presentation" cellpadding="0" cellspacing="0" border="0">
                        <tr>
                            <td align="center" style="border-radius: 12px; background: linear-gradient(135deg, #1a8fb8 0%, #0f3a50 100%); box-shadow: 0 4px 12px rgba(26, 143, 184, 0.3);">
                                <a href="{verification_url}" target="_blank" style="display: inline-block; padding: 16px 40px; font-size: 16px; font-weight: 600; color: #ffffff; text-decoration: none; border-radius: 12px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                                    ✓ Verify Email Address
                                </a>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
        
        <div style="background-color: #f9fafb; border-left: 4px solid #00d4ff; padding: 20px; border-radius: 8px; margin: 30px 0;">
            <p style="margin: 0 0 10px 0; color: #6b7280; font-size: 14px; line-height: 1.5;">
                <strong style="color: #374151;">Can't click the button?</strong><br>
                Copy and paste this link into your browser:
            </p>
            <p style="margin: 0; color: #1a8fb8; font-size: 13px; word-break: break-all;">
                <a href="{verification_url}" style="color: #1a8fb8; text-decoration: none;">{verification_url}</a>
            </p>
        </div>
        
        <p style="margin: 0; color: #9ca3af; font-size: 14px; line-height: 1.6;">
            ⏱️ This verification link will expire in <strong>24 hours</strong>.
        </p>
        """
        
        html_content = EmailService.render_template(
            "email_base.html",
            subject="Verify your ProductSnap account",
            content=content
        )
        
        text_content = f"""
        Welcome to LightClick Studio!
        
        {greeting}
        
        Thanks for signing up! Please verify your email address by clicking the link below:
        
        {verification_url}
        
        This link will expire in 24 hours.
        """
        
        await EmailService.send_email(
            to_email,
            "Verify your LightClick Studio account ✓",
            html_content,
            text_content
        )
    
    @staticmethod
    async def send_password_reset_email(to_email: str, token: str, user_name: Optional[str] = None):
        """Send password reset link."""
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        greeting = f"Hi {user_name}," if user_name else "Hi,"
        
        content = f"""
        <h2 style="margin: 0 0 20px 0; color: #111827; font-size: 28px; font-weight: 700; line-height: 1.3;">
            Reset Your Password 🔐
        </h2>
        <p style="margin: 0 0 20px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
            {greeting}
        </p>
        <p style="margin: 0 0 30px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
            We received a request to reset your password for your LightClick Studio account.
            Click the button below to create a new password:
        </p>
        
        <!-- CTA Button -->
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" style="margin: 30px 0;">
            <tr>
                <td align="center" style="border-radius: 12px; background: linear-gradient(135deg, #1a8fb8 0%, #0f3a50 100%); box-shadow: 0 4px 12px rgba(26, 143, 184, 0.3);">
                    <a href="{reset_url}" target="_blank" style="display: inline-block; padding: 16px 40px; font-size: 16px; font-weight: 600; color: #ffffff; text-decoration: none; border-radius: 12px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                        🔑 Reset Password
                    </a>
                </td>
            </tr>
        </table>
        
        <div style="background-color: #f9fafb; border-left: 4px solid #00d4ff; padding: 20px; border-radius: 8px; margin: 30px 0;">
            <p style="margin: 0 0 10px 0; color: #6b7280; font-size: 14px; line-height: 1.5;">
                <strong style="color: #374151;">Can't click the button?</strong><br>
                Copy and paste this link into your browser:
            </p>
            <p style="margin: 0; color: #1a8fb8; font-size: 13px; word-break: break-all;">
                <a href="{reset_url}" style="color: #1a8fb8; text-decoration: none;">{reset_url}</a>
            </p>
        </div>
        
        <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 20px; border-radius: 8px; margin: 30px 0;">
            <p style="margin: 0; color: #92400e; font-size: 14px; line-height: 1.6;">
                ⚠️ <strong>Security Notice:</strong> This link will expire in <strong>1 hour</strong>.<br>
                If you didn't request a password reset, please ignore this email or contact support if you're concerned.
            </p>
        </div>
        """
        
        html_content = EmailService.render_template(
            "email_base.html",
            subject="Reset your LightClick Studio password",
            content=content
        )
        
        text_content = f"""
        Reset Your Password
        
        {greeting}
        
        We received a request to reset your password. Click the link below to create a new password:
        
        {reset_url}
        
        This link will expire in 1 hour.
        
        If you didn't request a password reset, you can safely ignore this email.
        """
        
        await EmailService.send_email(
            to_email,
            "Reset your LightClick Studio password 🔐",
            html_content,
            text_content
        )
    
    @staticmethod
    async def send_job_completion_email(
        to_email: str,
        user_name: Optional[str],
        job_id: str,
        mode: str
    ):
        """Send email notification when a job completes."""
        job_url = f"{settings.FRONTEND_URL}/library?job={job_id}"
        greeting = f"Hi {user_name}," if user_name else "Hi,"
        
        # Mode-specific emoji and description
        mode_info = {
            "Studio White": {"emoji": "📸", "desc": "professional white background"},
            "Model Try-On": {"emoji": "👔", "desc": "model try-on"},
            "Lifestyle Scene": {"emoji": "🏠", "desc": "lifestyle scene"}
        }
        info = mode_info.get(mode, {"emoji": "✨", "desc": mode.lower()})
        
        content = f"""
        <div style="text-align: center; margin: 0 0 30px 0;">
            <div style="display: inline-block; background: linear-gradient(135deg, #dcfce7 0%, #d1fae5 100%); padding: 15px 30px; border-radius: 50px; margin-bottom: 20px;">
                <span style="font-size: 32px;">{info['emoji']}</span>
            </div>
        </div>
        
        <h2 style="margin: 0 0 20px 0; color: #111827; font-size: 28px; font-weight: 700; line-height: 1.3; text-align: center;">
            Your Product Shot is Ready! 🎉
        </h2>
        
        <p style="margin: 0 0 20px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
            {greeting}
        </p>
        
        <div style="background: linear-gradient(135deg, #e0f2fe 0%, #cffafe 100%); border-radius: 12px; padding: 25px; margin: 30px 0; text-align: center;">
            <p style="margin: 0 0 10px 0; color: #0f3a50; font-size: 18px; font-weight: 600; line-height: 1.5;">
                Great news! Your AI generation is complete.
            </p>
            <p style="margin: 0; color: #154d6b; font-size: 16px; line-height: 1.5;">
                <strong>{mode}</strong> • {info['desc']}
            </p>
        </div>
        
        <!-- CTA Button -->
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" style="margin: 30px 0;">
            <tr>
                <td align="center" style="border-radius: 12px; background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);">
                    <a href="{job_url}" target="_blank" style="display: inline-block; padding: 16px 40px; font-size: 16px; font-weight: 600; color: #ffffff; text-decoration: none; border-radius: 12px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                        👁️ View Your Result
                    </a>
                </td>
            </tr>
        </table>
        
        <div style="background-color: #f9fafb; border: 2px dashed #d1d5db; padding: 25px; border-radius: 12px; margin: 30px 0; text-align: center;">
            <p style="margin: 0 0 15px 0; color: #6b7280; font-size: 14px; line-height: 1.6;">
                💡 <strong style="color: #374151;">Pro Tip:</strong> Love your result? Share it with your audience or download it for your store.
            </p>
            <p style="margin: 0; color: #9ca3af; font-size: 13px; line-height: 1.5;">
                Need another shot? Head to your dashboard to create more stunning product photos!
            </p>
        </div>
        """
        
        html_content = EmailService.render_template(
            "email_base.html",
            subject="Your LightClick Studio generation is complete!",
            content=content
        )
        
        text_content = f"""
        Your product shot is ready!
        
        {greeting}
        
        Great news! Your {mode} generation has completed successfully.
        
        View your result: {job_url}
        """
        
        await EmailService.send_email(
            to_email,
            f"Your LightClick Studio generation is complete! {info['emoji']}",
            html_content,
            text_content
        )


    @staticmethod
    async def send_support_message(
        user_email: str,
        user_name: str,
        subject: str,
        message: str,
        category: str = "General"
    ):
        """Send support message from user to admin."""
        support_email = getattr(settings, 'SUPPORT_EMAIL', settings.SMTP_FROM)
        
        content = f"""
        <h2 style="margin: 0 0 20px 0; color: #111827; font-size: 24px; font-weight: 700; line-height: 1.3;">
            📧 New Support Request
        </h2>
        
        <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <p style="margin: 0 0 10px 0; color: #374151; font-size: 14px;"><strong>From:</strong> {user_name} ({user_email})</p>
            <p style="margin: 0 0 10px 0; color: #374151; font-size: 14px;"><strong>Category:</strong> {category}</p>
            <p style="margin: 0; color: #374151; font-size: 14px;"><strong>Subject:</strong> {subject}</p>
        </div>
        
        <div style="background-color: #ffffff; border: 1px solid #e5e7eb; padding: 25px; border-radius: 8px; margin: 20px 0;">
            <h3 style="margin: 0 0 15px 0; color: #111827; font-size: 16px; font-weight: 600;">Message:</h3>
            <div style="white-space: pre-wrap; color: #374151; font-size: 14px; line-height: 1.6;">{message}</div>
        </div>
        
        <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; border-radius: 4px; margin: 20px 0;">
            <p style="margin: 0; color: #92400e; font-size: 13px; line-height: 1.5;">
                💡 <strong>Reply to:</strong> {user_email}<br>
                🕒 <strong>Sent:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
            </p>
        </div>
        """
        
        html_content = EmailService.render_template(
            "email_base.html",
            subject=f"Support Request: {subject}",
            content=content
        )
        
        text_content = f"""
        New Support Request
        
        From: {user_name} ({user_email})
        Category: {category}
        Subject: {subject}
        
        Message:
        {message}
        
        Reply to: {user_email}
        """
        
        await EmailService.send_email(
            support_email,
            f"[ProductSnap Support] {subject}",
            html_content,
            text_content
        )
        
        # Send confirmation email to user
        user_content = f"""
        <h2 style="margin: 0 0 20px 0; color: #111827; font-size: 24px; font-weight: 700; line-height: 1.3;">
            📬 Support Request Received
        </h2>
        <p style="margin: 0 0 20px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
            Hi {user_name},
        </p>
        <p style="margin: 0 0 30px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
            Thanks for reaching out! We've received your support request and will get back to you as soon as possible.
        </p>
        
        <div style="background-color: #f9fafb; border: 1px solid #e5e7eb; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <p style="margin: 0 0 10px 0; color: #6b7280; font-size: 14px;"><strong style="color: #374151;">Your request:</strong></p>
            <p style="margin: 0 0 5px 0; color: #6b7280; font-size: 14px;">Subject: {subject}</p>
            <p style="margin: 0; color: #6b7280; font-size: 14px;">Category: {category}</p>
        </div>
        
        <p style="margin: 0; color: #6b7280; font-size: 14px; line-height: 1.6;">
            ⏱️ Typical response time: <strong>24-48 hours</strong>
        </p>
        """
        
        user_html_content = EmailService.render_template(
            "email_base.html",
            subject="Support request received",
            content=user_content
        )
        
        user_text_content = f"""
        Support Request Received
        
        Hi {user_name},
        
        Thanks for reaching out! We've received your support request:
        
        Subject: {subject}
        Category: {category}
        
        We'll get back to you within 24-48 hours.
        """
        
        await EmailService.send_email(
            user_email,
            "Support request received ✓",
            user_html_content,
            user_text_content
        )


email_service = EmailService()
