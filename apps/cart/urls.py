from django.urls import path
from .views import CartDetailItemListView, CartAddItemView, CartItemUpdateView

urlpatterns = [
    path('',CartDetailItemListView.as_view(),name='cart-detail'),
    path('add/',CartAddItemView.as_view(),name='cart-add'),
    path('update/',CartItemUpdateView.as_view(),name='cart-update'),
]