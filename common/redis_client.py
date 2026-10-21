"""
Redis 연결 지점. 참조: 개발 기능 명세서 v2.0 1.3절 (WAS Zone, was-redis 10.10.2.6)

이 모듈 하나만 통해서 Redis에 접근한다. 다른 파일에서 redis.Redis(...)를
직접 생성하지 않는다.
"""
import redis
from django.conf import settings

redis_client = redis.Redis.from_url(
    getattr(settings, "REDIS_URL", "redis://10.10.2.6:6379/0"),
    decode_responses=True,
)
