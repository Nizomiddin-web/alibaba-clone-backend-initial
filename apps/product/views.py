from drf_spectacular import openapi
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiExample
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from product.filters import ProductFilters
from product.models import Category, Product, Color, Size, Image
from product.permissions import IsProductOwner, HasCategoryPermission
from product.serializers import CategorySerializer, ProductSerializer, ProductUpdateSerializer, ProductCreateSerializer
from share.permissions import GeneratePermissions


# Create your views here.

@extend_schema_view(
    list=extend_schema(
          summary="List of All Category",
          request=CategorySerializer,
          responses={
              200:CategorySerializer,
          }
    ),
    create = extend_schema(
        summary="Create a category",
        description="This is api for create a category",
        request=CategorySerializer,
        responses={
            201:CategorySerializer
        }
    ),
    retrieve = extend_schema(
        summary="Get a category"
    ),
    products = extend_schema(
        summary="Products a category"
    )
)
class CategoryViewSet(GeneratePermissions,ModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    # permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action=='products':
            return [HasCategoryPermission()]
        return super().get_permissions()

    @action(detail=True,methods=['get'])
    def products(self,request,*args,**kwargs):
        category = self.get_object()
        products = category.products.all()
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductSerializer(page,many=True)
            return self.get_paginated_response(serializer.data)
        return Response({
            "count": 0,
            "results": []
        })

@extend_schema_view(
    update=extend_schema(
        summary="Product Update",
        request=ProductUpdateSerializer,
        responses={
            200:ProductUpdateSerializer
        }
    ),
    partial_update=extend_schema(
        summary="Product Partial Update",
        request=ProductUpdateSerializer,
        responses={
            200:ProductUpdateSerializer
        }
    )
)
class ProductViewSet(GeneratePermissions,ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter,DjangoFilterBackend]
    filterset_class = ProductFilters
    search_fields = ['title','description']

    def get_serializer_class(self):
        if self.action in ['update','partial_update']:
            return ProductUpdateSerializer
        elif self.action == 'create':
            return ProductCreateSerializer
        return super().get_serializer_class()
