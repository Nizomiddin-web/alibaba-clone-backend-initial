
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_email(user_email,otp_code):
    send_mail(
        'Xush kelibsiz!',
        otp_code,
        'reactspringgood@gmail.com',
        [user_email],
        fail_silently=False
    )
    return 200