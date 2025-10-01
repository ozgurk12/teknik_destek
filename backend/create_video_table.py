import asyncio
import asyncpg
from app.core.config import settings

async def create_table():
    # Database connection
    conn = await asyncpg.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        database=settings.POSTGRES_DB
    )

    try:
        # Create table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS video_generations (
                id SERIAL PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                prompt TEXT NOT NULL,
                image_urls JSON DEFAULT '[]',
                duration INTEGER DEFAULT 30,
                style VARCHAR(100) DEFAULT 'cinematic',
                music_genre VARCHAR(100),
                status VARCHAR(50) DEFAULT 'pending',
                video_url VARCHAR(500),
                error_message TEXT,
                external_job_id VARCHAR(200),
                processing_started_at TIMESTAMP WITH TIME ZONE,
                processing_completed_at TIMESTAMP WITH TIME ZONE,
                created_by UUID NOT NULL REFERENCES users(id),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE
            )
        """)

        # Create indexes
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_video_generations_created_by
            ON video_generations(created_by)
        """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_video_generations_status
            ON video_generations(status)
        """)

        print("✅ video_generations table created successfully!")

        # Check if table exists
        result = await conn.fetchval("""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_name = 'video_generations'
        """)

        if result > 0:
            print(f"✅ Table verified - exists in database")
        else:
            print("❌ Table creation failed")

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(create_table())