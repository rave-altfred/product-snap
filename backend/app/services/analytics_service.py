"""PostHog Analytics Service

Tracks backend events like job completion, subscription changes, etc.
"""
from typing import Optional, Dict, Any
import posthog
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    """PostHog analytics client wrapper."""
    
    def __init__(self):
        """Initialize PostHog client."""
        if settings.POSTHOG_API_KEY:
            posthog.api_key = settings.POSTHOG_API_KEY
            posthog.host = settings.POSTHOG_HOST
            logger.info("PostHog analytics initialized")
        else:
            logger.warning("PostHog API key not configured, analytics disabled")
    
    def is_enabled(self) -> bool:
        """Check if analytics is enabled."""
        return bool(settings.POSTHOG_API_KEY)
    
    def capture(
        self,
        user_id: str,
        event: str,
        properties: Optional[Dict[str, Any]] = None
    ):
        """Capture an analytics event.
        
        Args:
            user_id: User ID (email or UUID)
            event: Event name (e.g., "job_completed", "subscription_upgraded")
            properties: Additional event properties
        """
        if not self.is_enabled():
            return
        
        try:
            posthog.capture(
                distinct_id=user_id,
                event=event,
                properties=properties or {}
            )
            logger.info(f"PostHog event captured: {event} for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to capture PostHog event: {e}")
    
    def identify(
        self,
        user_id: str,
        properties: Optional[Dict[str, Any]] = None
    ):
        """Identify a user with properties.
        
        Args:
            user_id: User ID (email or UUID)
            properties: User properties (email, name, subscription_tier, etc.)
        """
        if not self.is_enabled():
            return
        
        try:
            posthog.identify(
                distinct_id=user_id,
                properties=properties or {}
            )
            logger.info(f"PostHog user identified: {user_id}")
        except Exception as e:
            logger.error(f"Failed to identify user in PostHog: {e}")
    
    def flush(self):
        """Flush pending events to PostHog.
        
        Call this before application shutdown or in long-running workers
        to ensure all events are sent.
        """
        if not self.is_enabled():
            return
        
        try:
            posthog.flush()
            logger.info("PostHog events flushed")
        except Exception as e:
            logger.error(f"Failed to flush PostHog events: {e}")


# Singleton instance
analytics = AnalyticsService()
