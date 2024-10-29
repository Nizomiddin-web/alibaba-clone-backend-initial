from django.shortcuts import render
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from share.enums import UserRole
from share.utils import OTPService
from user.models import BuyerUser, Group, SellerUser
from user.serializers import UserSerializer
from user.services import EmailService


# Create your views here.

class SignUpView(APIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            role = serializer.validated_data['user_trade_role']
            group = Group.objects.filter(name=role).first()
            if group:
                user.groups = group
                user.save()
                if role==UserRole.BUYER.value:
                    BuyerUser.objects.create(user=user)
                elif role==UserRole.SELLER.value:
                    SellerUser.objects.create(user=user)

            redis_conn = OTPService.get_redis_conn()
            if redis_conn.exists(f"{user.phone_number}:otp_secret"):
                secret_token = redis_conn.get(f"{user.phone_number}:otp_secret").decode()
            else:
                otp_code,secret_token = OTPService.generate_otp(phone_number_or_email=user.phone_number)
                try:
                    EmailService.send_email(email=user.email,otp_code=otp_code)
                except Exception:
                    redis_conn = OTPService.get_redis_conn()
                    redis_conn.delete(f"{user.phone_number}:otp_secret")
                    redis_conn.delete(f"{user.phone_number}:otp")
            data = {
                    "phone_number":user.phone_number,
                    "otp_secret":secret_token
                }
            return Response(data=data,status=status.HTTP_201_CREATED)
        print(request.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

