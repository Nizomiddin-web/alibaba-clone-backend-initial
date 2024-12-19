from django.urls import path

from payment.views import PaymentInitialApiView, PaymentConfirmApiView

urlpatterns = [
    path('<uuid:id>/initiate/',PaymentInitialApiView.as_view(),name='payment-initiate'),
    path('<uuid:id>/confirm/',PaymentConfirmApiView.as_view(),name='payment-confirm'),
]