from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.translation import gettext as _
from share.enums import UserRole
from share.utils import OTPService
from user.models import BuyerUser, Group, SellerUser
from user.serializers import UserSerializer
from share.utils import send_email,generate_otp,get_redis_conn
from rest_framework import generics
User = get_user_model()

# Create your views here.
redis_conn = get_redis_conn()

class SignUpView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    def post(self,request,*args,**kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            if User.objects.filter(phone_number=serializer.validated_data['phone_number'], is_verified=True).exists():
                return Response({'detail': _("User with this phone number already exists!")},
                                status=status.HTTP_409_CONFLICT)
            if User.objects.filter(email=serializer.validated_data['email'],is_verified=True).exists():
                return Response({'detail':_("User with this email already exists!")})
            user = serializer.save()
            role = serializer.validated_data['user_trade_role']
            group = Group.objects.filter(name=role).first()
            if group:
                user.groups.set([group])
                user.save()
                if role==UserRole.BUYER.value:
                    BuyerUser.objects.create(user=user)
                elif role==UserRole.SELLER.value:
                    SellerUser.objects.create(user=user)
            if redis_conn.exists(f"{user.phone_number}:otp_secret"):
                secret_token = redis_conn.get(f"{user.phone_number}:otp_secret").decode()
            else:
                otp_code,secret_token = generate_otp(phone_number_or_email=user.phone_number)
                try:
                    send_email(email=user.email,otp_code=otp_code)
                except Exception:
                    redis_conn.delete(f"{user.phone_number}:otp_secret")
                    redis_conn.delete(f"{user.phone_number}:otp")
            data = {
                    "phone_number":user.phone_number,
                    "otp_secret":secret_token
                }
            return Response(data=data,status=status.HTTP_201_CREATED)
        print(request.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

