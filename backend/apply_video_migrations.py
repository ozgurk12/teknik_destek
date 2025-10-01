import asyncio
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection parameters
DB_USER = os.getenv("POSTGRES_USER", "pgadmin")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "K12P0stgr32025!!**")
DB_HOST = os.getenv("POSTGRES_HOST", "172.16.15.222")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "edupage_kids")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

async def apply_migrations():
    """Apply all missing columns to video_generations table."""

    # Create async engine
    engine = create_async_engine(DATABASE_URL)

    migrations = [
        # Add parsed_content field
        "ALTER TABLE video_generations ADD COLUMN IF NOT EXISTS parsed_content JSON;",

        # Add kazanim_details field
        "ALTER TABLE video_generations ADD COLUMN IF NOT EXISTS kazanim_details JSON;",

        # Add curriculum_details field
        "ALTER TABLE video_generations ADD COLUMN IF NOT EXISTS curriculum_details JSON;",
    ]

    async with engine.begin() as conn:
        for migration in migrations:
            print(f"Applying: {migration}")
            try:
                await conn.execute(text(migration))
                print("✓ Success")
            except Exception as e:
                print(f"✗ Error: {e}")

        # Check current columns
        print("\nChecking current table structure:")
        result = await conn.execute(text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'video_generations'
            ORDER BY ordinal_position
        """))

        columns = result.fetchall()
        print("\nCurrent columns in video_generations table:")
        for col_name, col_type in columns:
            print(f"  - {col_name}: {col_type}")

    await engine.dispose()
    print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    asyncio.run(apply_migrations())