from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from cart.models import Cart, CartItem
from cart.serializers import CartDetailItemListSerializer, CartItemRequestSerializer
from product.models import Product
from share.permissions import GeneratePermissions


# Create your views here.

class CartDetailItemListView(GeneratePermissions,generics.ListAPIView):
    serializer_class = CartDetailItemListSerializer
    queryset = Cart.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        cart = Cart.objects.filter(user=self.request.user).first()
        return cart.cartItems.all()

class CartAddItemView(GeneratePermissions,generics.CreateAPIView):
    serializer_class = CartItemRequestSerializer
    queryset = CartItem.objects.all()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_id = serializer.validated_data.get('product_id')
        quantity = serializer.validated_data.get('quantity')

        if not Product.objects.filter(id=product_id).exists():
            return Response(data={"detail":"Product Not Found"},status=status.HTTP_404_NOT_FOUND)
        product = Product.objects.get(id=product_id)
        if product.quantity<quantity:
            return Response('error',status=status.HTTP_400_BAD_REQUEST)
        cart,created = Cart.objects.get_or_create(user=request.user)
        cart_item,item_created = CartItem.objects.get_or_create(
            product=product,
            cart=cart
        )
        if not item_created:
            cart_item.quantity=quantity
            cart_item.save()
        else:
            cart_item.quantity=quantity
            cart_item.save()
        cart_items = cart.cartItems.all().order_by('product')
        serializer = CartDetailItemListSerializer(instance=cart_items,many=True)
        return Response(serializer.data,status=status.HTTP_201_CREATED)

class CartItemUpdateView(GeneratePermissions,generics.UpdateAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemRequestSerializer
    permission_classes = [IsAuthenticated,]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_id = serializer.validated_data.get('product_id')
        quantity = serializer.validated_data.get('quantity')
        if not Product.objects.filter(id=product_id).exists():
            return Response(data={"detail":"Product Not Found"},status=status.HTTP_404_NOT_FOUND)
        product = Product.objects.get(id=product_id)
        cart = Cart.objects.get(user=request.user)
        cart_item = CartItem.objects.get(product=product,cart=cart)
        cart_item.quantity=quantity
        cart_item.save()
        cart_items = cart.cartItems.all().order_by('product')
        serializer = CartDetailItemListSerializer(instance=cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
