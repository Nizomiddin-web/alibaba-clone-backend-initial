from django.contrib.auth import get_user_model
from django.db import models

from product.models import Product

User = get_user_model()
# Create your models here.

class Cart(models.Model):
    user = models.ForeignKey(User,null=True,blank=True,on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=0)
    total = models.DecimalField(default=0.00,max_digits=10,decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"User: {self.user} Cart count: {self.count}"


class CartItem(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,null=True,related_name='cartItems')
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"Cart: {self.cart} Item: {self.product.title}"