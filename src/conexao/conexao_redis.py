from typing import Optional
from src.config.config import Config
import redis


class ConexaoRedis:

    def __init__(self):
        self.__host = Config.URL_REDIS
        self.__port = Config.PORTA_REDIS
        self.__db = Config.DB_REDIS
        self.__cliente_redis = redis.Redis(
            host=self.__host,
            port=self.__port,
            db=self.__db,
            decode_responses=True
        )

    def is_member(self, set_name: str, value: str) -> bool:
        return bool(self.__cliente_redis.sismember(set_name, value))

    def add_member(self, set_name: str, value: str, ttl_seconds: Optional[int] = None):
        self.__cliente_redis.sadd(set_name, value)
        if ttl_seconds:
            aux_key = f'ttl:{set_name}:{value}'
            self.__cliente_redis.setex(aux_key, ttl_seconds, "1")

    def close(self):
        try:
            self.__cliente_redis.close()
        except Exception:
            pass
