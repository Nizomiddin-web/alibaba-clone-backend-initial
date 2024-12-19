from django.urls import path

from payment.views import PaymentInitialApiView, PaymentConfirmApiView, PaymentCreateWithLinkApiView

urlpatterns = [
    path('<uuid:id>/initiate/',PaymentInitialApiView.as_view(),name='payment-initiate'),
    path('<uuid:id>/confirm/',PaymentConfirmApiView.as_view(),name='payment-confirm'),
    path('<uuid:id>/create/link/',PaymentCreateWithLinkApiView.as_view(),name='payment-create-link'),
]