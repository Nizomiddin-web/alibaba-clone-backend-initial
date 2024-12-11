from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from product.models import Category, Product, Color, Size, Image
from user.serializers import  UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = ['id','name','icon','is_active','created_at','parent','children']
        extra_kwargs = {'id':{'read_only':True}}
    def get_children(self,obj):
        return CategorySerializer(obj.children.all(),many=True).data

class ProductSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10,decimal_places=2,coerce_to_string=False)
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
        price = serializers.DecimalField(max_digits=10,decimal_places=2,coerce_to_string=False)
        colors = ColorSerializer(many=True, required=False)
        images = ImageSerializer(many=True,read_only=True)
        sizes = SizeSerializer(many=True, required=False)
        uploaded_images = serializers.ListField(
            child=serializers.ImageField(), required=False,write_only=True
        )
        class Meta:
            model = Product
            fields = [
                'id', 'seller', 'title', 'description', 'price', 'quantity', 'category',
                'colors', 'sizes', 'uploaded_images','images', 'views', 'created_at'
            ]
            read_only_fields = ['id','seller', 'views', 'created_at','images']

        def validate_price(self,price):
            if price<0:
                return ValidationError("Price 0 dan kichik bo'lmasligi kerak!")
            return price


        def create(self, validated_data):
            colors_data = validated_data.pop('colors',[])
            sizes_data = validated_data.pop('sizes',[])
            uploaded_images = validated_data.pop('uploaded_images',[])
            seller = self.context['request'].user

            product = Product.objects.create(seller=seller, **validated_data)

            for color_data in colors_data:
                color, _ = Color.objects.get_or_create(**color_data)
                product.colors.add(color)

            for size_data in sizes_data:
                size, _ = Size.objects.get_or_create(**size_data)
                product.sizes.add(size)

            for image in uploaded_images:
                Image.objects.create(product=product,image=image)

            return product

class ProductDetailSerializer(serializers.ModelSerializer):
    colors = ColorSerializer(many=True,read_only=True)
    sizes = SizeSerializer(many=True,read_only=True)
    images = ImageSerializer(many=True,read_only=True)
    category = CategorySerializer(read_only=True)
    seller = UserSerializer(read_only=True)
    class Meta:
        model=Product
        fields = ['id','category','seller','title','description','price','images','colors','sizes','quantity','views']



class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields = ['id', 'category', 'seller', 'title', 'description', 'price', 'image', 'quantity', 'views']
        extra_kwargs = {'seller':{"read_only":True},'views':{'read_only':True}}

