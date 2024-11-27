from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from product.models import Category, Product, Color, Size, Image
from user.serializers import SellerSerializer, UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = ['id','name','icon','is_active','created_at','parent','children']
        extra_kwargs = {'id':{'read_only':True}}
    def get_children(self,obj):
        return CategorySerializer(obj.children.all(),many=True).data

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    seller = UserSerializer()
    class Meta:
        model = Product
        fields = ['id','category','seller','title','description','price','image','quantity','views']

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = '__all__'
        extra_kwargs = {'id': {'read_only': True}}

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model=Size
        fields = '__all__'
        extra_kwargs = {'id':{'read_only':True}}

class ImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    class Meta:
        model = Image
        fields = ['id','image']
        # extra_kwargs = {'id': {'read_only': True}}


class ProductCreateSerializer(serializers.ModelSerializer):
        colors = ColorSerializer(many=True)
        sizes = SizeSerializer(many=True)
        # uploaded_images = serializers.ListField(
        #     child=serializers.ImageField(), required=False,write_only=True
        # )
        class Meta:
            model = Product
            fields = [
                'id', 'seller', 'title', 'description', 'price', 'quantity', 'category',
                'colors', 'sizes', 'views', 'created_at'
            ]
            read_only_fields = ['id','seller', 'views', 'created_at']

        def validate_price(self,price):
            if price<0:
                return ValidationError("Price 0 dan kichik bo'lmasligi kerak!")
            return price


        def create(self, validated_data):
            print(validated_data)
            colors_data = validated_data.pop('colors')
            sizes_data = validated_data.pop('sizes')
            # uploaded_images = validated_data.pop('uploaded_images',[])
            seller = self.context['request'].user

            print(colors_data)
            print(sizes_data)
            # print(uploaded_images)
            print(seller)
            product = Product.objects.create(seller=seller, **validated_data)

            for color_data in colors_data:
                color, _ = Color.objects.get_or_create(**color_data)
                print(color)
                product.colors.add(color)

            for size_data in sizes_data:
                size, _ = Size.objects.get_or_create(**size_data)
                print(size)
                product.sizes.add(size)

            # for image in uploaded_images:
            #     Image.objects.create(product_id=product,image=image)

            return product


class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields = ['id', 'category', 'seller', 'title', 'description', 'price', 'image', 'quantity', 'views']
        extra_kwargs = {'seller':{"read_only":True},'views':{'read_only':True}}

