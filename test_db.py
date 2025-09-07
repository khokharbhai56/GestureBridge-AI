#!/usr/bin/env python3
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from backend.database import db
    print("Attempting to connect to database...")
    result = db.connect()
    if result:
        print("✅ Database connected successfully!")
        print("Database stats:", db.get_database_stats())
    else:
        print("❌ Database connection failed!")
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
