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
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView, TokenVerifyView)
from core import settings
from core.settings import DEBUG

urlpatterns = [
    path("admin/", admin.site.urls),
    path("",lambda _:JsonResponse({"detail":"Healthy"}),name="health"),
    path("api/",include(
        [
            #Token Generate
            path('token/', TokenObtainPairView.as_view(), name="token-obtain-pair"),
            path('refresh/', TokenRefreshView.as_view(), name="token-refresh"),
            path('token/verify/', TokenVerifyView.as_view(), name='token-verify'),

            #Apps path
            path("users/",include('user.urls')),
            path("products/",include('product.urls')),
            path("cart/",include('cart.urls')),
            path("orders/",include('order.urls')),
            path("payment/",include('payment.urls')),
            path("notifications/",include('notification.urls')),
            path("coupons/",include('coupon.urls')),
            path("wishlist/",include('wishlist.urls')),
            # path("share/",include('share.urls')),

            #Swagger path
            path("schema/",SpectacularAPIView.as_view(),name="schema"),
            path("redoc/",SpectacularRedocView.as_view(),name="redoc"),
            path("swagger/",SpectacularSwaggerView.as_view(),name="swagger-ui"),


        ]
    )),
]

if DEBUG:
    urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)