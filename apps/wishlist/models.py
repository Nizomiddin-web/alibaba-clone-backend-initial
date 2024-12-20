from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import models

from product.models import Product

User = get_user_model()
# Create your models here.

class Wishlist(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid4)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='wishlists')
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='wishlists')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'wishlist'
        verbose_name = 'Wishlist'
        verbose_name_plural = 'Wishlists'
        ordering = ['-created_at']

    def __str__(self):
        return f"User:{self.created_by} and Product {self.product}"