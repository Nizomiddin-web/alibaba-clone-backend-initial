from django.urls import path, include
from rest_framework.routers import DefaultRouter

from product.views import CategoryViewSet

router = DefaultRouter()
router.register('categories',CategoryViewSet,basename='categories')

urlpatterns = [
    path('',include(router.urls))
]