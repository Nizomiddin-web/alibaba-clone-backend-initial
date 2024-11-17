from rest_framework import serializers

from product.models import Category, Product
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