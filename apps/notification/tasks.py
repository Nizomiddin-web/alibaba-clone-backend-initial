from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


@shared_task
def send_notification_task(email_seller,order):
    message_to_buyer = render_to_string('emails/send_notification_message_to_buyer.html',context={
        'email':order.user.email,
        'order_id':order.id
    })

    message_to_seller = render_to_string('email/send_notification_message_to_seller.html',context={
        'email':email_seller,
        'user_name':order.user.username,
        'order_id': order.id,
        'title':'test title'
    })

    email_message_to_buyer = EmailMessage(
        "Notification to Buyer",
        message_to_buyer,
        settings.EMAIL_HOST_USER,
        [order.user.email]
    )

    email_message_to_seller = EmailMessage(
        "Notification to Seller",
        message_to_seller,
        settings.EMAIL_HOST_USER,
        [email_seller]
    )
    email_message_to_buyer.content_subtype='html'
    email_message_to_seller.content_subtype='html'
    try:
        email_message_to_buyer.send(fail_silently=False)
        email_message_to_seller.send(fail_silently=False)
        return 200
    except Exception as e:
        print(f"buyerga Email jo'natishda xatolik yuz berdi {e}")
        return 400


