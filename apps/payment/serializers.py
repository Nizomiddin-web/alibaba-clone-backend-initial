from django.utils.datetime_safe import datetime
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class PaymentInitialSerializer(serializers.Serializer):
    card_number = serializers.CharField(max_length=16)
    expiry_month = serializers.CharField(max_length=2)
    expiry_year = serializers.CharField(max_length=4)
    cvc = serializers.CharField(max_length=3)

    def validate_expiry_year(self,expiry_year):
        if int(expiry_year)>=datetime.now().year:
            return expiry_year
        raise ValidationError(detail=[f"{expiry_year} karta yil muddati tugagan!"])

class PaymentConfirmApiRequestSerializer(serializers.Serializer):
    client_secret = serializers.CharField(max_length=200)