from django.urls import path
from .views import SignUpView, VerifyView, LoginView, UsersMeView, ChangePasswordView

urlpatterns = [
    path('register/',SignUpView.as_view(),name='sign-up'),
    path('register/verify/<str:otp_secret>/',VerifyView.as_view(),name='verify-otp'),
    path('login/',LoginView.as_view(),name='login'),
    path('change/password/',ChangePasswordView.as_view(),name='change-password'),
    path('me/',UsersMeView.as_view(),name='me')
]