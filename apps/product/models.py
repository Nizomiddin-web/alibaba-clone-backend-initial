from uuid import uuid4

from django.db import models

from user.models import SellerUser, User


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid4)
    description = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract=True



class Category(BaseModel):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self',on_delete=models.CASCADE,related_name='children',null=True,blank=True)
    icon = models.ImageField("product/category/icons/",null=True,blank=True)
    is_active = models.BooleanField(default=False)
    class Meta:
        db_table='category'
        verbose_name='Category'
        verbose_name_plural='Categories'
        ordering = ['-created_at']


    def __str__(self):
        return self.name

class Color(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid4)
    name=models.CharField(max_length=255)
    hex_value = models.TextField()

    def __str__(self):
        return self.name

class Size(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid4)
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name

class Product(BaseModel):
    title = models.CharField(max_length=255)
    seller = models.ForeignKey(User,on_delete=models.CASCADE,related_name="products")
    colors = models.ForeignKey(Color,on_delete=models.SET_NULL,related_name="products",null=True,blank=True)
    sizes = models.ForeignKey(Size,on_delete=models.SET_NULL,related_name="products",null=True,blank=True)
    price = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    quantity = models.IntegerField(default=0)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name="products")
    image = models.ImageField(upload_to="product/images/",null=True,blank=True)
    views = models.IntegerField(default=0)

    class Meta:
        db_table='product'
        verbose_name='Product'
        verbose_name_plural='Products'
        ordering=['-created_at']

    def __str__(self):
        return self.title
