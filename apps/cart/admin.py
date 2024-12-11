from django.contrib import admin
from .models import Cart,CartItem
# Register your models here.

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user','count','total']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['product','cart','quantity']