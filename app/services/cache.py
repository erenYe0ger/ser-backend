import json

from redis.asyncio import Redis

from app.core.config import settings


# Create a shared async Redis client using the configured Redis URL
redis_client = Redis.from_url(settings.REDIS_URL)


async def get_cached_result(file_hash: str) -> dict | None:
    # Look up the cached value using the file hash as the key
    cached_data = await redis_client.get(file_hash)

    # Return None if no cached result exists
    if cached_data is None:
        return None

    # Parse the JSON string back into a Python dictionary
    return json.loads(cached_data)


async def set_cached_result(
    file_hash: str,
    result: dict,
    ttl_seconds: int = 3600,
) -> None:
    # Convert the result dictionary into a JSON string
    serialized_result = json.dumps(result)

    # Store the JSON data in Redis with the specified TTL
    await redis_client.set(
        file_hash,
        serialized_result,
        ex=ttl_seconds,
    )