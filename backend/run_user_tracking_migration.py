#!/usr/bin/env python
"""
Run migration to add user tracking to activities and daily plans
"""
import asyncio
import sys
from pathlib import Path
from sqlalchemy import text

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import async_engine

async def run_migration():
    """Execute migration SQL to add user tracking fields"""

    async with async_engine.begin() as conn:
        print("🔄 Starting migration: Add user tracking to activities...")

        try:
            # Check if columns already exist
            check_query = """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'etkinlikler'
            AND column_name IN ('custom_instructions', 'created_by_id', 'created_by_username', 'created_by_fullname')
            """
            result = await conn.execute(text(check_query))
            existing_columns = [row[0] for row in result]

            if len(existing_columns) == 4:
                print("✅ User tracking columns already exist in etkinlikler table")
            else:
                # Add columns to etkinlikler table
                print("📝 Adding columns to etkinlikler table...")

                if 'custom_instructions' not in existing_columns:
                    await conn.execute(text("""
                        ALTER TABLE etkinlikler
                        ADD COLUMN IF NOT EXISTS custom_instructions TEXT
                    """))
                    print("  ✓ Added custom_instructions column")

                if 'created_by_id' not in existing_columns:
                    await conn.execute(text("""
                        ALTER TABLE etkinlikler
                        ADD COLUMN IF NOT EXISTS created_by_id UUID
                    """))
                    print("  ✓ Added created_by_id column")

                if 'created_by_username' not in existing_columns:
                    await conn.execute(text("""
                        ALTER TABLE etkinlikler
                        ADD COLUMN IF NOT EXISTS created_by_username VARCHAR(100)
                    """))
                    print("  ✓ Added created_by_username column")

                if 'created_by_fullname' not in existing_columns:
                    await conn.execute(text("""
                        ALTER TABLE etkinlikler
                        ADD COLUMN IF NOT EXISTS created_by_fullname VARCHAR(200)
                    """))
                    print("  ✓ Added created_by_fullname column")

                # Add foreign key constraint
                await conn.execute(text("""
                    ALTER TABLE etkinlikler
                    ADD CONSTRAINT fk_etkinlikler_created_by
                    FOREIGN KEY (created_by_id)
                    REFERENCES users(id)
                    ON DELETE SET NULL
                """))
                print("  ✓ Added foreign key constraint")

                # Create index
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_etkinlikler_created_by_id
                    ON etkinlikler(created_by_id)
                """))
                print("  ✓ Created index on created_by_id")

            # Check gunluk_planlar table
            check_query = """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'gunluk_planlar'
            AND column_name IN ('created_by_id', 'created_by_username', 'created_by_fullname')
            """
            result = await conn.execute(text(check_query))
            existing_columns = [row[0] for row in result]

            if len(existing_columns) == 3:
                print("✅ User tracking columns already exist in gunluk_planlar table")
            else:
                # Add columns to gunluk_planlar table
                print("📝 Adding columns to gunluk_planlar table...")

                if 'created_by_id' not in existing_columns:
                    await conn.execute(text("""
                        ALTER TABLE gunluk_planlar
                        ADD COLUMN IF NOT EXISTS created_by_id UUID
                    """))
                    print("  ✓ Added created_by_id column")

                if 'created_by_username' not in existing_columns:
                    await conn.execute(text("""
                        ALTER TABLE gunluk_planlar
                        ADD COLUMN IF NOT EXISTS created_by_username VARCHAR(100)
                    """))
                    print("  ✓ Added created_by_username column")

                if 'created_by_fullname' not in existing_columns:
                    await conn.execute(text("""
                        ALTER TABLE gunluk_planlar
                        ADD COLUMN IF NOT EXISTS created_by_fullname VARCHAR(200)
                    """))
                    print("  ✓ Added created_by_fullname column")

                # Add foreign key constraint
                try:
                    await conn.execute(text("""
                        ALTER TABLE gunluk_planlar
                        ADD CONSTRAINT fk_gunluk_planlar_created_by
                        FOREIGN KEY (created_by_id)
                        REFERENCES users(id)
                        ON DELETE SET NULL
                    """))
                    print("  ✓ Added foreign key constraint")
                except Exception as e:
                    if "already exists" in str(e):
                        print("  ℹ Foreign key constraint already exists")
                    else:
                        raise

                # Create index
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_gunluk_planlar_created_by_id
                    ON gunluk_planlar(created_by_id)
                """))
                print("  ✓ Created index on created_by_id")

            print("\n✅ Migration completed successfully!")
            print("\nNext steps:")
            print("1. Restart the backend server")
            print("2. New activities and plans will now track user information")
            print("3. Existing activities will show as created by 'Unknown'")

        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            raise

async def main():
    """Main function"""
    print("\n=== User Tracking Migration ===\n")

    try:
        await run_migration()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    finally:
        await async_engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())