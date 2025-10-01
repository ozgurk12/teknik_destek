import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.security import get_password_hash

async def reset_admin_password():
    """Reset admin password with argon2 hash"""

    # Create database connection
    engine = create_engine(settings.DATABASE_URL.replace("+asyncpg", ""))

    # New password
    new_password = "admin123"
    hashed_password = get_password_hash(new_password)
    print(f"Generated hash type: {'argon2' if hashed_password.startswith('$argon2') else 'bcrypt'}")

    # Update admin password
    with engine.connect() as conn:
        result = conn.execute(
            text("UPDATE users SET hashed_password = :password WHERE username = 'admin'"),
            {"password": hashed_password}
        )
        conn.commit()
        print(f"Updated {result.rowcount} user(s)")
        print(f"Admin password has been reset to: {new_password}")
        print(f"New hash: {hashed_password[:50]}...")

if __name__ == "__main__":
    asyncio.run(reset_admin_password())