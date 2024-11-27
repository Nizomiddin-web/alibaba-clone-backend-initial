from django.urls import path, include
from rest_framework.routers import DefaultRouter

from product.views import CategoryViewSet, ProductViewSet

router = DefaultRouter()
router.register('categories',CategoryViewSet,basename='categories')
router.register('',ProductViewSet,basename='products')

urlpatterns = [
    path('',include(router.urls))
]