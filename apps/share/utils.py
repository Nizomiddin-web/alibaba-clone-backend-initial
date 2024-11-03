import random
import string
import uuid
from email.policy import default
from secrets import token_urlsafe
# apps/share/utils.py

from typing import Union

import redis
from decouple import config
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMessage

from django.template.loader import render_to_string

from apps.user.exceptions import OTPException, SecretTokenException
from user.models import Group
from user.models import User, Policy

REDIS_HOST = config('REDIS_HOST',default=None)
REDIS_PORT = config('REDIS_PORT',default=None)
REDIS_DB = config('REDIS_DB',default=None)

def add_permissions(obj: Union[User, Group, Policy], permissions: list[str]):
    def get_perm(perm: str) -> list:
        app_label, codename = perm.split('.')
        try:
            model = codename.split('_')[1]
            content_type = ContentType.objects.get(app_label=app_label, model=model)
            permission, _ = Permission.objects.get_or_create(
                codename=codename,
                content_type=content_type,
            )
        except (IndexError, ContentType.DoesNotExist):
            # permission, _ = Permission.objects.get_or_create(
            #     codename=codename
            # )
            return None
        return permission

    permissions_to_add = filter(None, map(get_perm, permissions))

    if isinstance(obj, User):
        obj.user_permissions.clear()
        obj.user_permissions.add(*permissions_to_add)
    elif isinstance(obj, Group) or isinstance(obj, Policy):
        obj.permissions.clear()
        obj.permissions.add(*permissions_to_add)

class SendEmailService:
    @staticmethod
    def send_email(email,otp_code):
        subject = "Welcome to Our Service!"
        message = render_to_string('emails/send_otp_code.html',{
            'email':email,
            'otp_code':otp_code
        })
        email = EmailMessage(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [email]
        )
        email.content_type='html'
        email.send(fail_silently=False)

def send_email(email,otp_code):
        subject = "Welcome to Our Service!"
        message = render_to_string('emails/send_otp_code.html',{
            'email':email,
            'otp_code':otp_code
        })
        try:
            email = EmailMessage(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [email]
            )
            email.content_type='html'
            email.send(fail_silently=False)
            return True
        except Exception:
            return False

class OTPService:
    @classmethod
    def get_redis_conn(cls)->redis.Redis:
        return redis.Redis(host=REDIS_HOST,port=REDIS_PORT,db=REDIS_DB)

    @classmethod
    def generate_otp(cls,phone_number_or_email:str,expire_in:int=120,check_if_exists:bool=True):
        redis_conn = cls.get_redis_conn()
        otp_code = "".join(random.choices(string.digits,k=6))
        secret_token = token_urlsafe()

        #set secret_token to redis
        redis_conn.set(f"{phone_number_or_email}:otp_secret",secret_token,ex=expire_in)

        otp_hash = make_password(f"{secret_token}:{otp_code}")
        key = f"{phone_number_or_email}:otp"

        if check_if_exists and redis_conn.exists(key):
            ttl = redis_conn.ttl(key)
            raise OTPException(
                f"Sizda yaroqli OTP kodingiz bor .{ttl} soniyadan keyin qayta urinib ko'ring.",ttl
            )
        redis_conn.set(key,otp_hash,ex=expire_in)
        return otp_code,secret_token

    @classmethod
    def check_otp(cls,phone_number_or_email:str,otp_code:str,otp_secret:str)->None:
        redis_conn = cls.get_redis_conn()
        stored_hash = redis_conn.get(f"{phone_number_or_email}:otp")
        if not stored_hash or not check_password(f"{otp_secret}:{otp_code}",stored_hash.decode()):
            raise OTPException("Yaroqsiz otp kodi.")

    @classmethod
    def generate_token(cls)->str:
        return str(uuid.uuid4())

def get_redis_conn():
        return redis.Redis(host=REDIS_HOST,port=REDIS_PORT,db=REDIS_DB)

def generate_otp(phone_number_or_email:str,expire_in:int=120,check_if_exists:bool=True):
        redis_conn = OTPService.get_redis_conn()
        otp_code = "".join(random.choices(string.digits,k=6))
        secret_token = token_urlsafe()

        #set secret_token to redis
        redis_conn.set(f"{phone_number_or_email}:otp_secret",secret_token,ex=expire_in)

        otp_hash = make_password(f"{secret_token}:{otp_code}")
        key = f"{phone_number_or_email}:otp"

        if check_if_exists and redis_conn.exists(key):
            ttl = redis_conn.ttl(key)
            raise OTPException(
                f"Sizda yaroqli OTP kodingiz bor .{ttl} soniyadan keyin qayta urinib ko'ring.",ttl
            )
        redis_conn.set(key,otp_hash,ex=expire_in)
        return otp_code,secret_token


def check_otp(phone_number_or_email: str, otp_code: str, otp_secret: str) -> None:
    redis_conn = get_redis_conn()
    otp_secret1 = redis_conn.get(f"{phone_number_or_email}:otp_secret")
    if otp_secret1:
        otp_secret1 = otp_secret1.decode('utf-8')
        if otp_secret!=otp_secret1:
            raise SecretTokenException("Yaroqsiz OTP SECRET")
    stored_hash = redis_conn.get(f"{phone_number_or_email}:otp")
    if not stored_hash or not check_password(f"{otp_secret}:{otp_code}",stored_hash.decode()):
        raise OTPException("Yaroqsiz otp kodi")