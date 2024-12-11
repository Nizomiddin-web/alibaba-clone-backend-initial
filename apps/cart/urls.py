from django.urls import path
from .views import CartDetailItemListView, CartAddItemView, CartItemUpdateView, CartGetTotalView, CartItemDeleteView, \
    CartEmptyView

urlpatterns = [
    path('',CartDetailItemListView.as_view(),name='cart-detail'),
    path('add/',CartAddItemView.as_view(),name='cart-add'),
    path('update/',CartItemUpdateView.as_view(),name='cart-update'),
    path('total/',CartGetTotalView.as_view(),name='cart-total'),
    path('remove/<uuid:product_id>/',CartItemDeleteView.as_view(),name='cart-total'),
    path('empty/',CartEmptyView.as_view(),name='cart-total'),
]