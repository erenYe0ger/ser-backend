# migrate.py

import asyncio
import os

import asyncpg
from dotenv import load_dotenv


async def migrate():
    load_dotenv()

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL not found in .env")

    # Convert SQLAlchemy URL to asyncpg-compatible URL
    database_url = database_url.replace(
        "postgresql+asyncpg://",
        "postgresql://",
        1,
    )

    connect_kwargs = {}
    if "neon.tech" in database_url:
        connect_kwargs["ssl"] = "require"

    conn = await asyncpg.connect(database_url, **connect_kwargs)

    try:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR PRIMARY KEY,
                email VARCHAR,
                name VARCHAR,
                picture VARCHAR,
                user_type VARCHAR NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT NOW()
            )
            """
        )
        print("✓ users table created or already exists")

        await conn.execute(
            """
            ALTER TABLE predictions
            ADD COLUMN IF NOT EXISTS user_id VARCHAR
            """
        )
        print("✓ user_id column added to predictions or already exists")

        await conn.execute(
            """
            ALTER TABLE predictions
            ADD COLUMN IF NOT EXISTS audio_url VARCHAR
            """
        )
        print("✓ audio_url column added to predictions or already exists")

        await conn.execute(
            """
            ALTER TABLE predictions
            ADD COLUMN IF NOT EXISTS timeline_data JSONB
            """
        )
        print("✓ timeline_data column added to predictions or already exists")

        print("✓ Migration completed successfully")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(migrate())