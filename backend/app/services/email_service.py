import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails."""
    
    @staticmethod
    async def send_email(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ):
        """Send an email via SMTP."""
        message = MIMEMultipart("alternative")
        message["From"] = settings.SMTP_FROM
        message["To"] = to_email
        message["Subject"] = subject
        
        # Add text and HTML parts
        if text_content:
            part1 = MIMEText(text_content, "plain")
            message.attach(part1)
        
        part2 = MIMEText(html_content, "html")
        message.attach(part2)
        
        try:
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                use_tls=settings.SMTP_TLS
            )
            logger.info(f"Email sent to {to_email}")
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            raise
    
    @staticmethod
    async def send_verification_email(to_email: str, token: str, user_name: Optional[str] = None):
        """Send email verification link."""
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        
        greeting = f"Hi {user_name}," if user_name else "Hi,"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4F46E5;">Welcome to ProductSnap!</h2>
                <p>{greeting}</p>
                <p>Thanks for signing up! Please verify your email address by clicking the button below:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" 
                       style="background-color: #4F46E5; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Verify Email
                    </a>
                </div>
                <p style="color: #666; font-size: 14px;">
                    Or copy and paste this link into your browser:<br>
                    <a href="{verification_url}">{verification_url}</a>
                </p>
                <p style="color: #666; font-size: 14px;">
                    This link will expire in 24 hours.
                </p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to ProductSnap!
        
        {greeting}
        
        Thanks for signing up! Please verify your email address by clicking the link below:
        
        {verification_url}
        
        This link will expire in 24 hours.
        """
        
        await EmailService.send_email(
            to_email,
            "Verify your ProductSnap account",
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
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #10B981;">Your product shot is ready!</h2>
                <p>{greeting}</p>
                <p>Great news! Your <strong>{mode}</strong> generation has completed successfully.</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{job_url}" 
                       style="background-color: #10B981; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        View Result
                    </a>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Your product shot is ready!
        
        {greeting}
        
        Great news! Your {mode} generation has completed successfully.
        
        View your result: {job_url}
        """
        
        await EmailService.send_email(
            to_email,
            "Your ProductSnap generation is complete!",
            html_content,
            text_content
        )


email_service = EmailService()
