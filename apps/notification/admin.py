from django.contrib import admin

from notification.models import Notification


# Register your models here.

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id','user','message','created_at']
    list_filter = ['created_at']
