import redis
import sys
from datetime import timedelta
from config_settings import Settings
setting = Settings()

def redis_connect() -> redis.client.Redis:
    try:
        client = redis.Redis(
            host=setting.redis_host,
            port=6379,
            db=0,
            socket_timeout=5,
        )
        ping = client.ping()
        if ping is True:
            return client
    except redis.AuthenticationError:
        print("AuthenticationError")
        sys.exit(1)


client = redis_connect()

def get_routes_from_cache(key: str) -> str:
    """Get data from redis."""

    val = client.get(key)
    return val


def set_routes_to_cache(key: str, value: str) -> bool:
    """Set data to redis."""

    state = client.setex(key, timedelta(seconds=60), value=value, )
    return state

def delete_routes_from_cache(key: str) -> bool:
    """Delete data from redis."""

    state = client.delete(key)
    return state