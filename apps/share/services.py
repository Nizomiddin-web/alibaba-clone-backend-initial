from datetime import timedelta
import uuid
import redis
from core.settings import REDIS_URL
from share.enums import TokenType


class TokenService:

    @classmethod
    def get_redis_client(cls)->redis.Redis:
        return redis.Redis.from_url(REDIS_URL)

    @classmethod
    def get_valid_tokens(cls,user_id:uuid.UUID,token_type:TokenType)->set:
        redis_client = cls.get_redis_client()
        token_key = f"user:{user_id}:{token_type}"
        valid_tokens = redis_client.smembers(token_key)
        return valid_tokens

    @classmethod
    def add_token_to_redis(cls,user_id:uuid.UUID,token:str,token_type:TokenType,lifetime:timedelta)->None:
        redis_client = cls.get_redis_client()
        token_key = f"user:{user_id}:{token_type}"
        valid_tokens = cls.get_valid_tokens(user_id,token_type)
        if valid_tokens:
            pass
        redis_client.sadd(token_key,token)
        redis_client.expire(token_key,lifetime)

    @classmethod
    def delete_tokens(cls,user_id:uuid.UUID,token_type:TokenType)->None:
        redis_client = cls.get_redis_client()
        token_key = f"user:{user_id}:{token_type}"
        valid_tokens = redis_client.smembers(token_key)
        if valid_tokens is not None:
            (redis_client.delete(token_key))

class ClientSecretService:
    @classmethod
    def get_redis_client(cls)->redis.Redis:
        return redis.Redis.from_url(REDIS_URL)

    @classmethod
    def get_valid_client_secret(cls,user_id:uuid.UUID)->set:
        redis_client = cls.get_redis_client()
        token_key = f"user:{user_id}:client_secret"
        valid_client_secrets = redis_client.smembers(token_key)
        return valid_client_secrets

    @classmethod
    def add_client_secret_to_redis(cls,user_id:uuid.UUID,client_secret:str,lifetime:timedelta)->None:
        redis_client = cls.get_redis_client()
        token_key = f"user:{user_id}:client_secret"
        valid_client_secrets = cls.get_valid_client_secret(user_id)
        if valid_client_secrets:
            pass
        else:
            redis_client.sadd(token_key,client_secret)
            redis_client.expire(token_key,lifetime)

    @classmethod
    def delete_client_secret(cls,user_id:uuid.UUID)->None:
        redis_client = cls.get_redis_client()
        token_key = f"user:{user_id}:client_secret"
        valid_client_secrets = cls.get_valid_client_secret(user_id)
        if valid_client_secrets is not None:
            (redis_client.delete(token_key))

