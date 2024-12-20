from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import models
User = get_user_model()
# Create your models here.

class NotificationType(models.TextChoices):
    ORDER = "order","Order"
    PAYMENT = "payment","Payment"
    GENERAL = "general","General"

class Notification(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid4)
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='notifications')
    type = models.CharField(max_length=30,choices=NotificationType.choices)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notification'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']