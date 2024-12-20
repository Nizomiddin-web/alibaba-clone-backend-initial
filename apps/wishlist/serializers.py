
from rest_framework import serializers

from product.models import Product
from product.serializers import ProductSerializer
from wishlist.models import Wishlist


class WishlistSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(write_only=True)
    product = ProductSerializer(read_only=True)
    class Meta:
        model = Wishlist
        fields = ['id','product_id','created_by','product','created_at']
        extra_kwargs = {
            'id':{'read_only':True},
            'created_by':{'read_only':True},
            'product':{'read_only':True},
            'created_at':{'read_only':True}

                        }
    def create(self, validated_data):
        # product_id dan mahsulotni olish
        product_id = validated_data.pop('product_id')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError({"product_id": ['Product not found.']})
        # Wishlist obyektini yaratish
        validated_data['product'] = product
        # validated_data['created_by'] = product
        if Wishlist.objects.filter(created_by=validated_data['created_by'],product=product).exists():
            raise serializers.ValidationError({'detail':'Product is already in the wishlist.'})
        return Wishlist.objects.create(**validated_data)

