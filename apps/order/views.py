
from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from cart.models import Cart
from order.models import Order, OrderItem
from order.permissions import CheckOrderUser
from order.serializers import OrderCheckoutRequestSerializer, OrderCheckoutResponseSerializer
from share.permissions import GeneratePermissions


# Create your views here.

class OrderCheckoutView(GeneratePermissions,CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderCheckoutRequestSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            return Response(data={"detail":"Sizning savatingiz bo'sh!"},status=status.HTTP_409_CONFLICT)
        elif not cart.cartItems.all():
            return Response(data={"detail": "Sizning savatingiz bo'sh!"}, status=status.HTTP_409_CONFLICT)
        order = Order.objects.filter(user=request.user).first()
        if order and order.status=='pending':
            return Response(data={"detail":"sizda to'lov qilinmagan buyurtma mavjud"},status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save(user=request.user)
        for cart_item in cart.cartItems.all():
            OrderItem.objects.create(
                product=cart_item.product,
                order=order,
                quantity = cart_item.quantity,
                price = cart_item.product.price*cart_item.quantity
            )
        serializer = OrderCheckoutResponseSerializer(instance=order)
        return Response(serializer.data,status=status.HTTP_201_CREATED)