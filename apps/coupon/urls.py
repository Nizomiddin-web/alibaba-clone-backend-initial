from django.urls import path

from coupon.views import CouponListCreateApiView

urlpatterns = [
    path('',CouponListCreateApiView.as_view(),name='coupon-list')
]