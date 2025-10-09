#!/usr/bin/env python3
"""
Script to create test users for Playwright E2E testing.
Creates a basic user and a premium user.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models import User, Subscription, OAuthProvider
from app.models.subscription import SubscriptionPlan, SubscriptionStatus
from app.services.auth_service import AuthService
from datetime import datetime, timedelta
import uuid


def create_test_users(db: Session):
    """Create test users for E2E testing."""
    
    print("🔧 Creating test users for Playwright E2E testing...\n")
    
    # Test user credentials
    users_to_create = [
        {
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User",
            "is_premium": False,
            "description": "Basic test user"
        },
        {
            "email": "premium@example.com",
            "password": "premiumpass123",
            "full_name": "Premium Test User",
            "is_premium": True,
            "description": "Premium test user"
        }
    ]
    
    created_users = []
    
    for user_data in users_to_create:
        email = user_data["email"]
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        
        if existing_user:
            print(f"⚠️  User {email} already exists. Skipping...")
            
            # Update password if needed
            existing_user.password_hash = AuthService.hash_password(user_data["password"])
            existing_user.is_active = True
            existing_user.email_verified = True
            db.commit()
            
            print(f"✅ Updated password for {email}")
            created_users.append(existing_user)
            continue
        
        # Create new user
        user_id = str(uuid.uuid4())
        password_hash = AuthService.hash_password(user_data["password"])
        
        user = User(
            id=user_id,
            email=email,
            password_hash=password_hash,
            full_name=user_data["full_name"],
            oauth_provider=OAuthProvider.EMAIL,
            email_verified=True,  # Auto-verify test users
            is_active=True,
            is_admin=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(user)
        db.flush()
        
        # Create subscription
        if user_data["is_premium"]:
            subscription = Subscription(
                id=str(uuid.uuid4()),
                user_id=user.id,
                plan="pro_yearly",  # Use string value to match database enum
                status="active",
                current_period_start=datetime.utcnow(),
                current_period_end=datetime.utcnow() + timedelta(days=365),
                created_at=datetime.utcnow()
            )
        else:
            subscription = Subscription(
                id=str(uuid.uuid4()),
                user_id=user.id,
                plan="free",  # Use string value to match database enum
                status="active",
                current_period_start=datetime.utcnow(),
                current_period_end=None,
                created_at=datetime.utcnow()
            )
        
        db.add(subscription)
        db.commit()
        
        created_users.append(user)
        tier = "Premium (Pro)" if user_data["is_premium"] else "Free"
        print(f"✅ Created {user_data['description']}: {email} ({tier})")
    
    print("\n" + "="*60)
    print("📋 Test User Credentials Summary:")
    print("="*60)
    
    for user_data in users_to_create:
        tier = "PRO" if user_data["is_premium"] else "FREE"
        print(f"\n{user_data['description'].upper()}:")
        print(f"  Email:    {user_data['email']}")
        print(f"  Password: {user_data['password']}")
        print(f"  Tier:     {tier}")
    
    print("\n" + "="*60)
    print("✅ Test users are ready for Playwright testing!")
    print("\nUpdate your frontend/.env.test file with:")
    print("="*60)
    print("""
TEST_USER_EMAIL=test@example.com
TEST_USER_PASSWORD=testpassword123

TEST_PREMIUM_EMAIL=premium@example.com
TEST_PREMIUM_PASSWORD=premiumpass123
    """)
    print("="*60)
    
    return created_users


def main():
    """Main function."""
    print("\n" + "="*60)
    print("🚀 ProductSnap Test User Creation Script")
    print("="*60 + "\n")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create test users
        users = create_test_users(db)
        
        print(f"\n✅ Successfully created/updated {len(users)} test users!")
        print("\n💡 Tip: Run 'npm run test:ui' in the frontend directory to start testing.")
        
    except Exception as e:
        print(f"\n❌ Error creating test users: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
