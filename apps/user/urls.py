from django.urls import path
from .views import SignUpView, VerifyView, LoginView, UsersMeView, ChangePasswordView, ForgotPasswordView, \
    ForgotVerifyView, ResetPasswordView, LogOutView

urlpatterns = [
    path('register/',SignUpView.as_view(),name='sign-up'),
    path('register/verify/<str:otp_secret>/',VerifyView.as_view(),name='verify-otp'),
    path('login/',LoginView.as_view(),name='login'),
    path('change/password/',ChangePasswordView.as_view(),name='change-password'),
    path('password/forgot/',ForgotPasswordView.as_view(),name='forgot-password'),
    path('password/forgot/verify/<str:otp_secret>/',ForgotVerifyView.as_view(),name='forgot-password-verify'),
    path('password/reset/',ResetPasswordView.as_view(),name='reset-password'),
    path('logout/',LogOutView.as_view(),name='reset-password'),
    path('me/',UsersMeView.as_view(),name='me')
]