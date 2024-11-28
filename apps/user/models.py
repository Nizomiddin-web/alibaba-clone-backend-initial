from fcntl import FASYNC
from math import trunc
from uuid import uuid4

from django.db import models
from django.contrib.auth.models import AbstractUser, Permission

from user.manager import CustomUserManager


# Create your models here.

class Policy(models.Model):
    name = models.CharField(max_length=13,unique=True)
    permissions = models.ManyToManyField(Permission,blank=True,related_name='policies')
    is_active = models.BooleanField(default=False)
    created_by = models.ForeignKey('User',on_delete=models.SET_NULL,null=True,blank=True,related_name='created_policies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "policy"
        verbose_name = "Policy"
        verbose_name_plural = "Policies"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

class Group(models.Model):
   name = models.CharField(max_length=255)
   policies = models.ManyToManyField(Policy,blank=True,related_name='groups')
   permissions = models.ManyToManyField(Permission,blank=True,related_name='groups')
   is_active = models.BooleanField(default=True)
   created_by = models.ForeignKey('User',null=True,blank=True,on_delete=models.SET_NULL,related_name='created_groups')
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)

   class Meta:
       db_table = "group"
       verbose_name = "Group"
       verbose_name_plural="Groups"
       ordering = ['-created_at']

   def __str__(self):
        return self.name

class User(AbstractUser):
    id = models.UUIDField(primary_key=True,default=uuid4)
    phone_number = models.CharField(max_length=13)
    email = models.EmailField("Email Address")
    gender = models.CharField(max_length=10,null=True,blank=True)
    groups = models.ManyToManyField(Group,blank=True,related_name='users')
    policies = models.ManyToManyField(Policy,blank=True,related_name='users')
    is_verified = models.BooleanField(default=False)
    created_by = models.ForeignKey('self',null=True,blank=True,on_delete=models.SET_NULL,related_name='created_users')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    username = None

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()
    class Meta:
        db_table = 'user'
        verbose_name='User'
        verbose_name_plural='Users'
        ordering=['-created_at']

    def __str__(self):
        return self.phone_number


class AbstractClientUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    company = models.CharField(max_length=50, null=True, blank=True)
    bio = models.CharField(max_length=255, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    district = models.CharField(max_length=50, null=True, blank=True)
    street_address = models.CharField(max_length=50, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    second_phone_number = models.CharField(max_length=13, null=True, blank=True)
    building_number = models.CharField(max_length=50, null=True, blank=True)
    apartment_number = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract=True

class SellerUser(AbstractClientUser):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='seller_users')
    image = models.ImageField(upload_to="user/seller/image",null=True,blank=True)
    created_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name='created_sellers')

    class Meta:
        db_table = 'seller'
        verbose_name='Seller'
        verbose_name_plural='Sellers'
        ordering=['-created_at']


class BuyerUser(AbstractClientUser):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='buyer_users')
    image = models.ImageField(upload_to="user/buyer/image",null=True,blank=True)
    created_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name='created_buyers')
    class Meta:
        db_table = 'buyer'
        verbose_name = 'Buyer'
        verbose_name_plural = 'Buyers'
        ordering = ['-created_at']



