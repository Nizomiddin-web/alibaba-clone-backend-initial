from django.contrib import admin

from product.models import Category, Product,Color,Size


# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name','description','parent']
    search_fields = ['name']
    list_filter = ['created_at']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title','description']
    search_fields = ['title']
    list_filter = ['created_at']

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name']