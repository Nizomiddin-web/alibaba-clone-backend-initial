from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import models
User = get_user_model()
# Create your models here.

class DiscountTypeChoice(models.TextChoices):
    PERCENTAGE = 'percentage','Percentage'
    FIXED = 'fixed','Fixed'

class Coupon(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid4)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='coupons',null=True,blank=True)
    code = models.CharField(max_length=200)
    active = models.BooleanField(default=True)
    discount_type = models.CharField(max_length=200,choices=DiscountTypeChoice.choices,default=DiscountTypeChoice.PERCENTAGE)
    discount_value = models.DecimalField(max_digits=10,decimal_places=2)
    valid_from = models.DateTimeField(verbose_name="Qaysi sanadan amal qiladi")
    valid_until = models.DateTimeField(verbose_name="Qaysi sanagacha amal qiladi")
    max_uses = models.PositiveIntegerField(null=True,blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'coupon'
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'
        ordering = ['-created_at']