import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

async def check_users():
    async with AsyncSessionLocal() as session:
        # Check all users
        result = await session.execute(text("""
            SELECT email, username, role, full_name, id
            FROM users
            ORDER BY created_at
        """))
        users = result.fetchall()
        print('=== Tüm Kullanıcılar ===')
        for user in users:
            print(f'Email: {user.email}')
            print(f'Username: {user.username}')
            print(f'Role: {user.role}')
            print(f'Full Name: {user.full_name}')
            print(f'ID: {user.id}')
            print('-' * 40)

        # Check enum values
        result = await session.execute(text("""
            SELECT DISTINCT role FROM users
        """))
        roles = result.fetchall()
        print('\n=== Kullanılan Roller ===')
        for role in roles:
            print(f'Role: {role[0]}')

asyncio.run(check_users())