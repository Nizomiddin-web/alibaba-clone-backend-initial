from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers

from share.enums import UserRole
from user.models import SellerUser

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    user_trade_role = serializers.ChoiceField(choices=[UserRole.BUYER.value,UserRole.SELLER.value])
    confirm_password = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    class Meta:
        model = User
        fields = ['gender','first_name','last_name','phone_number','email','password','confirm_password','user_trade_role']

    def validate(self,data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        if password!=confirm_password:
            raise ValidationError({"detail":"Password and Confirm Password must be same"})
        return data

    def create(self, validated_data):
        user = User.objects.filter(phone_number=validated_data['phone_number'],email=validated_data['email']).first()
        if user:
            return user
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            gender = validated_data['gender'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number = validated_data['phone_number']
        )
        return user