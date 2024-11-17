
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import filters, status
from product.models import Category
from product.permissions import IsProductOwner, HasCategoryPermission
from product.serializers import CategorySerializer, ProductSerializer


# Create your views here.

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    permission_classes = [IsAuthenticated]

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
