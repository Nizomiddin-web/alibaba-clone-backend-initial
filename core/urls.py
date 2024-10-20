"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView, TokenVerifyView)
from core import settings
from core.settings import DEBUG

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/",lambda _:JsonResponse({"detail":"Healthy"}),name="health"),
    path('api/token/',TokenObtainPairView.as_view(),name="token-obtain-pair"),
    path('api/refresh/',TokenRefreshView.as_view(),name="token-refresh"),
    path('api/token/verify/',TokenVerifyView.as_view(),name='token-verify')
]

if DEBUG:
    urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)