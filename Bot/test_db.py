import asyncio

from Bot.database.connection import create_pool


async def main():
    pool = await create_pool()

    print("PostgreSQL ga ulanish muvaffaqiyatli!")

    await pool.close()


if __name__ == "__main__":
    asyncio.run(main())