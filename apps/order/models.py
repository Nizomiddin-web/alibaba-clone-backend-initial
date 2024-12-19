from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import models

from product.models import Product

User = get_user_model()
# Create your models here.
class CountryChoice(models.TextChoices):
    UZBEKISTAN = "Uzbekistan","Uzbekistan"
    TURKMENISTAN = "Turkmenistan","Turkmenistan"
    QOZOGISTON = "Qozog'iston","Qozog'iston"

class PaymentChoice(models.TextChoices):
    CLICK = "Click","Click"
    PAYME = "Payme","Payme"
    CARD = "card","Card"
    PAYPAL = "Paypal","Paypal"

class StatusChoice(models.TextChoices):
    PENDING = "pending","Pending"
    PAID = "paid","Paid"
    CANCELED = "canceled","Canceled"
    DELIVERED = "delivered","Delivered"
    SHIPPED = 'shipped','Shipped'

# class Address(models.Model):
#     user = models.ForeignKey(User,on_delete=models.CASCADE)
#     country_region = models.CharField(max_length=200,choices=CountryChoice.choices)
#     city = models.CharField(max_length=200)
#     state_province_region=models.CharField(null=True,blank=True,max_length=200)
#     postal_zip_code = models.CharField(null=True,blank=True,max_length=200)
#     telephone_number = models.CharField(max_length=15)
#     address_line_1 = models.CharField(null=True,blank=True,max_length=200)
#     address_line_2 = models.CharField(null=True,blank=True,max_length=200)
#
#     def __str__(self):
#         return f"{self.country}#{self.city}"

class Shipping(models.Model):
    name = models.CharField(null=True,blank=True,max_length=200)
    time = models.TimeField(null=True,blank=True)
    price = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)

    def __str__(self):
        return self.name


class Order(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid4)
    status = models.CharField(max_length=20,choices=StatusChoice.choices,default=StatusChoice.PENDING)
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='orders')
    payment_method = models.CharField(max_length=20,choices=PaymentChoice.choices,null=True,blank=True)
    amount = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    country_region = models.CharField(max_length=200, choices=CountryChoice.choices,null=True)
    city = models.CharField(max_length=200,null=True)
    state_province_region = models.CharField(null=True, blank=True, max_length=200)
    postal_zip_code = models.CharField(null=True, blank=True, max_length=200)
    telephone_number = models.CharField(max_length=15,null=True)
    address_line_1 = models.CharField(null=True, blank=True, max_length=200)
    address_line_2 = models.CharField(null=True, blank=True, max_length=200)
    shipping = models.OneToOneField(Shipping,null=True,blank=True,on_delete=models.SET_NULL)
    is_paid = models.BooleanField(default=False)
    transaction_id = models.CharField(null=True,blank=True,max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'order'
        verbose_name='Order'
        verbose_name_plural='Orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order by: {self.user} # Id: {self.id}"

class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid4,editable=True)
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True)
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name="order_items")
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
