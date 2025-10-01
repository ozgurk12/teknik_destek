#!/usr/bin/env python
"""
Add user tracking columns to existing tables
"""
import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.db.session import async_engine

async def add_user_tracking_columns():
    """Add user tracking columns to etkinlikler and gunluk_planlar tables"""

    async with async_engine.begin() as conn:
        # Check and add columns to etkinlikler table
        print("Checking etkinlikler table...")

        # Check if columns exist
        result = await conn.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'etkinlikler'
            AND column_name IN ('custom_instructions', 'created_by_id', 'created_by_username', 'created_by_fullname')
        """))
        existing_columns = {row[0] for row in result}

        # Add missing columns to etkinlikler
        if 'custom_instructions' not in existing_columns:
            await conn.execute(text("""
                ALTER TABLE etkinlikler
                ADD COLUMN custom_instructions TEXT
            """))
            print("✓ Added custom_instructions to etkinlikler")

        if 'created_by_id' not in existing_columns:
            await conn.execute(text("""
                ALTER TABLE etkinlikler
                ADD COLUMN created_by_id UUID REFERENCES users(id) ON DELETE SET NULL
            """))
            print("✓ Added created_by_id to etkinlikler")

        if 'created_by_username' not in existing_columns:
            await conn.execute(text("""
                ALTER TABLE etkinlikler
                ADD COLUMN created_by_username VARCHAR(100)
            """))
            print("✓ Added created_by_username to etkinlikler")

        if 'created_by_fullname' not in existing_columns:
            await conn.execute(text("""
                ALTER TABLE etkinlikler
                ADD COLUMN created_by_fullname VARCHAR(200)
            """))
            print("✓ Added created_by_fullname to etkinlikler")

        # Check and add columns to gunluk_planlar table
        print("\nChecking gunluk_planlar table...")

        result = await conn.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'gunluk_planlar'
            AND column_name IN ('created_by_id', 'created_by_username', 'created_by_fullname')
        """))
        existing_columns = {row[0] for row in result}

        # Add missing columns to gunluk_planlar
        if 'created_by_id' not in existing_columns:
            await conn.execute(text("""
                ALTER TABLE gunluk_planlar
                ADD COLUMN created_by_id UUID REFERENCES users(id) ON DELETE SET NULL
            """))
            print("✓ Added created_by_id to gunluk_planlar")

        if 'created_by_username' not in existing_columns:
            await conn.execute(text("""
                ALTER TABLE gunluk_planlar
                ADD COLUMN created_by_username VARCHAR(100)
            """))
            print("✓ Added created_by_username to gunluk_planlar")

        if 'created_by_fullname' not in existing_columns:
            await conn.execute(text("""
                ALTER TABLE gunluk_planlar
                ADD COLUMN created_by_fullname VARCHAR(200)
            """))
            print("✓ Added created_by_fullname to gunluk_planlar")

        print("\n✅ Database migration completed successfully!")

async def main():
    """Main function"""
    print("\n=== Adding User Tracking Columns ===\n")

    try:
        await add_user_tracking_columns()
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())