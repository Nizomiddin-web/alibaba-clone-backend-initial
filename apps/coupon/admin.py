from django.contrib import admin

from coupon.models import Coupon


# Register your models here.

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['id','created_by','code']