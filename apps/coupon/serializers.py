from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from coupon.models import Coupon


class CouponListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id','created_by','code','active','discount_type','discount_value','valid_from','valid_until']

class CouponRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id','created_by','code','active','discount_type','discount_value','valid_from','valid_until','max_uses']
        read_only_fields = ['id','created_by','active']

class CouponUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id','created_by','code','active','discount_type','discount_value','valid_from','valid_until','max_uses']
        read_only_fields = ['id','created_by','created_at']

class CouponApplyRequestSerializer(serializers.Serializer):
    coupon_code = serializers.CharField(max_length=200)
    order_id = serializers.UUIDField()

    # def validate_coupon_code(self,coupon_code):
    #     coupon = Coupon.objects.filter(code=coupon_code).first()
    #     if now()>coupon.valid_until:
    #         raise ValidationError(detail={"coupon_code":["The coupon code has expired."]})
    #     elif now()<coupon.valid_from:
    #         raise ValidationError(detail={"coupon_code":["The coupon code is not yet valid."]})
    #     return coupon_code