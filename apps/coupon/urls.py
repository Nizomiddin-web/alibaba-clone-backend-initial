from django.urls import path

from coupon.views import CouponListCreateApiView, CouponUpdateDeleteApiView, CouponApplyApiView

urlpatterns = [
    path('',CouponListCreateApiView.as_view(),name='coupon-create-list'),
    path('<uuid:pk>/',CouponUpdateDeleteApiView.as_view(),name='coupon-update-delete'),
    path('apply/',CouponApplyApiView.as_view(),name='coupon-apply'),
]