from django.urls import path
from .views import SignUpView, VerifyView, LoginView

urlpatterns = [
    path('register/',SignUpView.as_view(),name='sign-up'),
    path('register/verify/<str:otp_secret>/',VerifyView.as_view(),name='verify-otp'),
    path('login/',LoginView.as_view(),name='login')
]