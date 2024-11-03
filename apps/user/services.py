import datetime
import enum

import uuid
from secrets import token_urlsafe
from typing import Union

import redis
from decouple import config
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError

from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken

from share.utils import get_redis_conn


class TokenType(enum.Enum):
    ACCESS = "access"
    REFRESH = "refresh"

REDIS_HOST = config('REDIS_HOST',None)
REDIS_PORT = config('REDIS_PORT',None)
REDIS_DB = config('REDIS_DB',None)

User = get_user_model()

class UserServie:
    @classmethod
    def authenticate(cls, email_or_phone_number: str, password: str, quiet=False) -> Union[ValidationError, User, None]:
       try:
           if "@" in email_or_phone_number:
               user = User.objects.get(email=email_or_phone_number)
           else:
               user = User.objects.get(phone_number = email_or_phone_number)
       except User.DoesNotExist:
           if not quiet:
               print("Xatolik user not found")
               return ValidationError('User not found')
       if not check_password(password,user.password):
           if not quiet:
               return ValidationError("Parol noto'g'ri")
           return None
       return user

    @classmethod
    def create_tokens(cls, user: User, access: str = None, refresh: str = None) -> dict[str, str]:
        if not access or not refresh:
            refresh_token = RefreshToken.for_user(user)
            access_token =  refresh_token.access_token
        else:
            refresh_token = refresh
            access_token = access

        return {
            "access":access_token,
            "refresh":refresh_token
        }


class TokenService:
    @classmethod
    def get_valid_tokens(cls, user_id: uuid.UUID, token_type: TokenType) -> set:
        redis_conn = get_redis_conn()
        return redis_conn.get(f"{user_id}:{token_type.value}")

    @classmethod
    def add_token_to_redis(
            cls,
            user_id: uuid.UUID,
            token: str,
            token_type: TokenType,
            expire_time: datetime.timedelta,
    ) -> None:
        redis_conn = get_redis_conn()
        key = f"{user_id}:{token_type.value}"
        redis_conn.set(key,token,ex=expire_time)

    @classmethod
    def delete_tokens(cls, user_id: uuid.UUID, token_type: TokenType) -> None:
        redis_conn = get_redis_conn()
        key = f"{user_id}:{token_type.value}"
        redis_conn.delete(key)