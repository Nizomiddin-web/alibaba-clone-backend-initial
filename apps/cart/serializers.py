from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from cart.models import CartItem
from product.models import Product
from product.serializers import ProductSerializer


class CartDetailItemListSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['product','quantity','price']
        extra_kwargs = {'price':{'read_only':True}}

    def get_price(self,cart_item):
        return cart_item.product.price * cart_item.quantity


class CartItemRequestSerializer(serializers.Serializer):
    product_id = serializers.UUIDField(required=True)
    quantity = serializers.IntegerField(required=True)

    def validate_quantity(self,quantity):
        if quantity>0:
            return  quantity
        raise ValidationError("Quantity error")

