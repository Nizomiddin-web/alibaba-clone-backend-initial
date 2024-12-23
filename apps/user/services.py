from typing import Union
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from share.enums import TokenType
from share.services import TokenService


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
               raise ValidationError('User not found')
       if not check_password(password,user.password):
           if not quiet:
               raise ValidationError("Parol noto'g'ri")
           return None
       return user

    @classmethod
    def create_tokens(cls, user: User, access: str = None, refresh: str = None, is_force_add_to_redis: bool = False) -> dict[str, str]:
        if not access or not refresh:
            refresh_token = RefreshToken.for_user(user)
            access =  str(getattr(refresh_token,'access_token'))
            refresh = str(refresh_token)

        valid_access_tokens = TokenService.get_valid_tokens(
            user_id=user.id,token_type=TokenType.ACCESS
        )
        if valid_access_tokens or is_force_add_to_redis:
            TokenService.add_token_to_redis(
                user_id=user.id,
                token=access,
                token_type=TokenType.ACCESS,
                expire_time=settings.SIMPLE_JWT.get("ACCESS_TOKEN_LIFETIME")
            )
        valid_refresh_tokens = TokenService.get_valid_tokens(
            user_id=user.id,
            token_type=TokenType.REFRESH
        )
        if valid_refresh_tokens or is_force_add_to_redis:
            TokenService.add_token_to_redis(
                user_id=user.id,
                token=refresh,
                token_type=TokenType.REFRESH,
                expire_time=settings.SIMPLE_JWT.get("REFRESH_TOKEN_LIFETIME")
            )
        return {
            "access":access,
            "refresh":refresh
        }