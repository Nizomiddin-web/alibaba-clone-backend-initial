from django.urls import path

from payment.views import PaymentInitialApiView

urlpatterns = [
    path('<uuid:id>/initiate/',PaymentInitialApiView.as_view(),name='payment-initiate'),
]