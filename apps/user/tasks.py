
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_welcome(user_email):
    send_mail(
        'Xush kelibsiz!',
        'Bizning saytga hush kelibsiz'
        'reactspringgood@gmail.com',
        [user_email],
        fail_silently=False
    )