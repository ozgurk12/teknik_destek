#!/usr/bin/env python
"""
Initialize user management system
Run this script to create user tables and default admin user
"""
import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.db.session import async_engine
from app.db.base import Base
from app.models.user import User, Module, user_modules
from app.core.security import get_password_hash
from app.models.user import UserRole
import uuid

async def create_tables():
    """Create all user-related tables"""
    # Import all models to ensure they're registered
    from app.models.user import User, Module, user_modules  # noqa

    async with async_engine.begin() as conn:
        # Create only user-related tables
        await conn.run_sync(Base.metadata.create_all, tables=[
            User.__table__,
            Module.__table__,
            user_modules
        ])
        print("✓ User tables created successfully")

async def create_default_modules():
    """Create default modules"""
    from app.db.session import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        # Check if modules already exist
        result = await session.execute(text("SELECT COUNT(*) FROM modules"))
        count = result.scalar()

        if count > 0:
            print("ℹ Modules already exist, skipping...")
            return

        modules_data = [
            {
                "name": "etkinlik_olusturma",
                "display_name": "Etkinlik Oluşturma",
                "description": "Etkinlik oluşturma ve düzenleme yetkisi"
            },
            {
                "name": "gunluk_plan",
                "display_name": "Günlük Plan",
                "description": "Günlük plan oluşturma ve düzenleme yetkisi"
            },
            {
                "name": "kazanim_yonetimi",
                "display_name": "Kazanım Yönetimi",
                "description": "Kazanım görüntüleme ve yönetim yetkisi"
            },
            {
                "name": "sablon_yonetimi",
                "display_name": "Şablon Yönetimi",
                "description": "Şablon oluşturma ve düzenleme yetkisi"
            },
            {
                "name": "raporlama",
                "display_name": "Raporlama",
                "description": "Rapor görüntüleme ve oluşturma yetkisi"
            },
            {
                "name": "kullanici_yonetimi",
                "display_name": "Kullanıcı Yönetimi",
                "description": "Kullanıcı oluşturma ve yönetim yetkisi (yönetici)"
            }
        ]

        for module_data in modules_data:
            module = Module(**module_data)
            session.add(module)

        await session.commit()
        print(f"✓ Created {len(modules_data)} default modules")

async def create_default_admin():
    """Create default admin user if no users exist"""
    from app.db.session import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        # Check if any user exists
        result = await session.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar()

        if count > 0:
            print("ℹ Users already exist, skipping admin creation...")
            return

        # Create default admin
        admin = User(
            id=uuid.uuid4(),
            email="admin@edupage.com",
            username="admin",
            full_name="System Administrator",
            hashed_password=get_password_hash("Admin123!"),
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )

        session.add(admin)
        await session.commit()

        print("✓ Default admin user created:")
        print("  Username: admin")
        print("  Password: Admin123!")
        print("  ⚠️  IMPORTANT: Change this password after first login!")

async def main():
    """Main initialization function"""
    print("\n=== EduPage Kids User Management System Initialization ===\n")

    try:
        # Create tables
        await create_tables()

        # Create default modules
        await create_default_modules()

        # Create default admin
        await create_default_admin()

        print("\n✅ User management system initialized successfully!")
        print("\nYou can now:")
        print("1. Login with the admin account")
        print("2. Create manager (yönetici) accounts")
        print("3. Managers can create teacher (kullanıcı) accounts")
        print("4. Assign modules to users based on their needs\n")

    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())