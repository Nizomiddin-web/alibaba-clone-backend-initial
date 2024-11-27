from django_filters import rest_framework as filters

from product.models import Product


class ProductFilters(filters.FilterSet):
    recommend_by_product_id = filters.UUIDFilter(field_name='id',method="get_recomment_by_product_id")
    class Meta:
        model = Product
        fields=['recommend_by_product_id']

    def get_recomment_by_product_id(self,queryset,name,value):
        if value:
            product  = queryset.filter(id=value).first()
            if product:
                category = product.category
                return category.products.all().exclude(id=value).order_by('-views')
            return queryset.none()
        return queryset
