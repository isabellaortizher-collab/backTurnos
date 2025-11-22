import time
from fastapi import HTTPException, status
from app.core.config import settings

_STORE = {}  # key -> (count, reset_ts)

def check_rate(key: str, limit: int, window_seconds: int = 60):
    now = time.time()
    count, reset = _STORE.get(key, (0, now + window_seconds))
    if now > reset:
        count = 0
        reset = now + window_seconds
    count += 1
    _STORE[key] = (count, reset)
    if count > limit:
        retry_after = int(reset - now)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Retry after {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)}
        )
