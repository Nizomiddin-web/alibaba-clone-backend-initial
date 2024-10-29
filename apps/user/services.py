import random
import string
import uuid
from secrets import token_urlsafe

import redis
from decouple import config
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from apps.user.exceptions import OTPException

REDIS_HOST = config('REDIS_HOST',None)
REDIS_PORT = config('REDIS_PORT',None)
REDIS_DB = config('REDIS_DB',None)

User = get_user_model()

class EmailService:
    @staticmethod
    def send_email(email,otp_code):
        subject = 'Welcome to Our Service!'
        message = render_to_string('emails/send_otp_code.html',{
            'email':email,
            'otp_code':otp_code
        })
        email =  EmailMessage(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [email]
        )
        email.content_type = 'html'
        email.send(fail_silently=False)

class OTPService:
    @classmethod
    def get_redis_conn(cls)->redis.Redis:
        return redis.Redis(host=REDIS_HOST,port=REDIS_PORT,db=REDIS_DB)

    @classmethod
    def generate_otp(cls,phone_number_or_email:str,expire_in:int=120,check_if_exists:bool=True)->tuple[str,str]:
        redis_conn =    cls.get_redis_conn()
        otp_code = "".join(random.choices(string.digits,k=6))
        secret_token = token_urlsafe()
        otp_hash = make_password(f"{secret_token}:{otp_code}")
        key = f"{[phone_number_or_email]}:otp"

        if check_if_exists and redis_conn.exists(key):
            ttl = redis_conn.ttl(key)
            raise OTPException(_("Sizda yaroqli OTP kodingiz bor. {ttl} soniyadan keyin qayta urinib koʻring.").format(ttl),ttl)
        redis_conn.set(key,otp_hash,ex=expire_in)
        return otp_code, secret_token

    @classmethod
    def check_otp(cls,email:str,otp_code:str,otp_secret:str)->None:
        redis_conn = cls.get_redis_conn()
        stored_hash = redis_conn.get(f"{email}:otp")

        if not stored_hash or not check_password(f"{otp_secret}:{otp_code}",stored_hash.decode()):
            raise OTPException(_("Yaroqsiz OTP kodi."))

    @classmethod
    def generate_token(cls)->str:
        return str(uuid.uuid4())