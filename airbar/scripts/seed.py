import asyncio
import bcrypt
from prisma import Prisma

async def seed():
    db = Prisma()
    await db.connect()

    # Create admin user
    hashed_password = bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt()).decode()

    try:
        await db.admin.create(
            data={
                'email': 'admin@airbar.com',
                'password': hashed_password
            }
        )
        print("Admin user created successfully")
    except Exception as e:
        print(f"Error creating admin user: {e}")

    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(seed())
