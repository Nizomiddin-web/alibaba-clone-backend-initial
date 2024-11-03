from django.urls import path
from .views import SignUpView, VerifyView

urlpatterns = [
    path('register/',SignUpView.as_view(),name='sign-up'),
    path('register/verify/<str:otp_secret>/',VerifyView.as_view(),name='verify-otp')
]