from django.contrib import admin

from user.models import User, Group, Policy


# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email','phone_number']

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['id','name','is_active']

@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ['id','name','is_active']