"""Initialize Production Database Tables"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base, engine
from app.models import *  # Import all models

def init_db():
    """Create all database tables."""
    print("Creating database tables...")
    print(f"Database URL: {engine.url}")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("✓ All tables created successfully!")
    print("\nCreated tables:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")

if __name__ == "__main__":
    init_db()
