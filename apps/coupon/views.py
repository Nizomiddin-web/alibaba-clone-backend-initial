from django.shortcuts import render
from django.views.generic import GenericViewError
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from urllib3 import request

from coupon.models import Coupon
from coupon.serializers import CouponListSerializer, CouponRequestSerializer
from share.permissions import GeneratePermissions


# Create your views here.

class CouponListCreateApiView(GeneratePermissions,ListAPIView,CreateAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponListSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method=='POST':
            return CouponRequestSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)