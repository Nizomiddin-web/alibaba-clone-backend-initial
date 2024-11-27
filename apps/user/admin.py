from django.contrib import admin

from user.models import User, Group, Policy, BuyerUser


# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id','first_name','email','phone_number']
    list_display_links = ['id','email']

@admin.register(BuyerUser)
class BuyerUserAdmin(admin.ModelAdmin):
    list_display = ['user']

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['id','name','is_active']

@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ['id','name','is_active']