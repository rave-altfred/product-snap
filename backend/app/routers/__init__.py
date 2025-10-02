# Import routers to make them available
from app.routers import auth, health, jobs, subscriptions, users, admin

__all__ = ["auth", "health", "jobs", "subscriptions", "users", "admin"]
