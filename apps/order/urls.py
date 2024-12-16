from django.urls import path

from order.views import OrderCheckoutView, OrderListApiView, OrderDetailApiView, OrderHistoryApiView

urlpatterns = [
    path('checkout/',OrderCheckoutView.as_view(),name='order-checkout'),
    path('',OrderListApiView.as_view(),name='order-list'),
    path('<uuid:pk>/',OrderDetailApiView.as_view(),name='order-list'),
    path('history/',OrderHistoryApiView.as_view(),name='order-history'),
]