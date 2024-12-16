import re
from math import trunc
from random import choices

from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from cart.models import Cart
from order.models import PaymentChoice, CountryChoice, Order, OrderItem


class OrderCheckoutRequestSerializer(serializers.ModelSerializer):
    payment_method = serializers.CharField()
    country_region = serializers.CharField()
    city = serializers.CharField()
    state_province_region = serializers.CharField()
    postal_zip_code = serializers.CharField()
    telephone_number = serializers.CharField(min_length=9,max_length=13,required=True)
    address_line_1 = serializers.CharField(max_length=200)
    address_line_2 = serializers.CharField(max_length=200,required=False)

    class Meta:
        model = Order
        fields = ['payment_method','country_region','city','state_province_region','postal_zip_code','telephone_number','address_line_1','address_line_2']

    def validate_payment_method(self,payment_method):
        if payment_method in PaymentChoice.values:
            return payment_method
        raise ValidationError(detail={"payment_method":[f"{payment_method} is not a valid choice"]})

    def validate_country_region(self,country_region):
        if country_region in CountryChoice.values:
            return country_region
        raise ValidationError(detail={"country_region":[f"{country_region} is not a valid choice"]})



class OrderCheckoutResponseSerializer(serializers.ModelSerializer):
    shipping_name = serializers.CharField(source='shipping.name',default=None)
    shipping_time = serializers.CharField(source='shipping.time',default=None)
    shipping_price = serializers.CharField(source='shipping.price',default=None)
    class Meta:
        model = Order
        fields = ['id','user','status','payment_method','order_items','country_region','city','state_province_region','postal_zip_code',
                  'telephone_number','address_line_1','address_line_2','shipping_name','shipping_time','shipping_price','is_paid']
