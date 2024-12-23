from django.utils.timezone import now
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from urllib3 import request

from coupon.models import Coupon, DiscountTypeChoice
from coupon.serializers import CouponListSerializer, CouponRequestSerializer, CouponUpdateSerializer, \
    CouponApplyRequestSerializer
from order.models import Order
from share.pagination import CustomPagination
from share.permissions import GeneratePermissions


# Create your views here.

class CouponListCreateApiView(GeneratePermissions,ListAPIView,CreateAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination


    def get_serializer_class(self):
        if self.request.method=='POST':
            return CouponRequestSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class CouponUpdateDeleteApiView(GeneratePermissions,DestroyAPIView,UpdateAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponUpdateSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch','delete']

class CouponApplyApiView(GeneratePermissions,APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CouponApplyRequestSerializer
    def post(self,request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order_id = serializer.validated_data.get('order_id')
        code = serializer.validated_data.get('coupon_code')
        order = Order.objects.filter(id=order_id,user=request.user).first()
        coupon = Coupon.objects.filter(code=code).first()
        if not order:
            return Response(data={"detail":"Buyurtma topilmadi yoki kirish huquqi yo'q."},status=status.HTTP_404_NOT_FOUND)
        if not coupon or not coupon.active or request.user in coupon.user.all():
            return Response(data={"coupon_code":"Coupon does not exist."},status=status.HTTP_400_BAD_REQUEST)
        elif now()>coupon.valid_until:
            return Response(data={"coupon_code":["The coupon code has expired."]},status=status.HTTP_400_BAD_REQUEST)
        elif now()<coupon.valid_from:
            return Response(data={"coupon_code":['The coupon code is not yet valid.']},status=status.HTTP_400_BAD_REQUEST)
        if coupon.discount_type==DiscountTypeChoice.PERCENTAGE:
            order.amount = order.amount - order.amount*coupon.discount_value/100
            order.save()
        elif coupon.discount_type==DiscountTypeChoice.FIXED:
            order.amount = order.amount-coupon.discount_value
            order.save()
        coupon.user.add(request.user)
        coupon.save()
        return Response(data={"detail":"Kupon muvaffaqiyatli qo'llandi."})