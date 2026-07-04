from slowapi import Limiter

from app.core.config import settings
from app.core.security import get_rate_limit_key

limiter = Limiter(
    key_func=get_rate_limit_key,
    storage_uri=settings.REDIS_URL,
)