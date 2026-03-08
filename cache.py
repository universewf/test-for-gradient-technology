import os
from dotenv import load_dotenv
from redis.asyncio import Redis

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis = Redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
