import asyncio
import json
import os
import sys

# Ensure backend app is in python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from app.models.db import Base, engine, AsyncSessionLocal
from app.core.logging import logger


async def seed_database():
    logger.info("Initializing ClaimFlow database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables verified and initialized successfully.")


if __name__ == "__main__":
    asyncio.run(seed_database())
