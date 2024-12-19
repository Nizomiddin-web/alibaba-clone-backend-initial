from django.urls import path

from payment.views import PaymentInitialApiView, PaymentConfirmApiView, PaymentCreateWithLinkApiView, \
    PaymentSuccessApiView, PaymentCancelApiView

urlpatterns = [
    path('<uuid:id>/initiate/',PaymentInitialApiView.as_view(),name='payment-initiate'),
    path('<uuid:id>/confirm/',PaymentConfirmApiView.as_view(),name='payment-confirm'),
    path('<uuid:id>/create/link/',PaymentCreateWithLinkApiView.as_view(),name='payment-create-link'),
    path('<uuid:id>/success/',PaymentSuccessApiView.as_view(),name='payment-success'),
    path('<uuid:id>/cancel/',PaymentCancelApiView.as_view(),name='payment-cancel'),
]