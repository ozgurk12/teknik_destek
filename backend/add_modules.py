#!/usr/bin/env python3
"""
Script to add new modules (Aylık Planlar and Video Oluşturma) to the database
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import AsyncSessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def add_modules():
    """Add new modules to the database"""
    async with AsyncSessionLocal() as session:
        try:
            # Add Aylık Planlar module
            await session.execute(text("""
                INSERT INTO modules (id, name, display_name, description, is_active, created_at)
                VALUES (
                    gen_random_uuid(),
                    'aylik_plan',
                    'Aylık Planlar',
                    'Aylık plan oluşturma ve yönetim yetkisi',
                    true,
                    NOW()
                ) ON CONFLICT (name) DO NOTHING
            """))

            # Add Video Generation module
            await session.execute(text("""
                INSERT INTO modules (id, name, display_name, description, is_active, created_at)
                VALUES (
                    gen_random_uuid(),
                    'video_generation',
                    'Video Oluşturma',
                    'Video oluşturma ve yönetim yetkisi',
                    true,
                    NOW()
                ) ON CONFLICT (name) DO NOTHING
            """))

            # Give ADMIN role users access to new modules
            await session.execute(text("""
                INSERT INTO user_modules (user_id, module_id, granted_by)
                SELECT u.id, m.id, u.id
                FROM users u
                CROSS JOIN modules m
                WHERE u.role = 'ADMIN'
                  AND m.name IN ('aylik_plan', 'video_generation')
                ON CONFLICT (user_id, module_id) DO NOTHING
            """))

            # Give YONETICI role users access to new modules
            await session.execute(text("""
                INSERT INTO user_modules (user_id, module_id, granted_by)
                SELECT u.id, m.id, u.id
                FROM users u
                CROSS JOIN modules m
                WHERE u.role = 'YONETICI'
                  AND m.name IN ('aylik_plan', 'video_generation')
                ON CONFLICT (user_id, module_id) DO NOTHING
            """))

            await session.commit()

            # Verify modules were added
            result = await session.execute(text("""
                SELECT name, display_name, description
                FROM modules
                WHERE name IN ('aylik_plan', 'video_generation')
            """))

            modules = result.fetchall()
            for module in modules:
                logger.info(f"✅ Module added: {module.name} - {module.display_name}")

            # Check which users have access
            result = await session.execute(text("""
                SELECT u.email, m.name
                FROM users u
                JOIN user_modules um ON u.id = um.user_id
                JOIN modules m ON m.id = um.module_id
                WHERE m.name IN ('aylik_plan', 'video_generation')
                ORDER BY u.email, m.name
            """))

            user_modules = result.fetchall()
            logger.info("\n📋 User module access:")
            for um in user_modules:
                logger.info(f"  - {um.email}: {um.name}")

            logger.info("\n✅ Modules successfully added!")

        except Exception as e:
            logger.error(f"Error adding modules: {e}")
            await session.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(add_modules())