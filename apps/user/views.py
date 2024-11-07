from datetime import timedelta
from functools import partial

from click import group
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.template.context_processors import request
from rest_framework import permissions, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.translation import gettext as _
from share.enums import UserRole
from share.permissions import GeneratePermissions
from share.utils import OTPService, check_otp
from user.models import BuyerUser, Group, SellerUser
from user.serializers import UserSerializer, VerifyCodeSerializer, LoginUserSerializer,\
    SellerSerializer, BuyerSerializer
from share.utils import generate_otp,get_redis_conn
from rest_framework import generics

from user.services import UserServie, TokenService, TokenType
from user.tasks import send_email

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
                return Response({'detail':_("User with this email already exists!")},status=status.HTTP_409_CONFLICT)
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
                    send_email.delay(email=user.email,otp_code=otp_code)
                except Exception:
                    redis_conn.delete(f"{user.phone_number}:otp_secret")
                    redis_conn.delete(f"{user.phone_number}:otp")
            data = {
                    "phone_number":user.phone_number,
                    "otp_secret":secret_token
                }
            print(otp_code)
            return Response(data=data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class VerifyView(generics.UpdateAPIView):
   serializer_class = VerifyCodeSerializer
   permission_classes = [AllowAny,]
   http_method_names = ['patch']

   def partial_update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp_secret = self.kwargs.get('otp_secret')
        if not otp_secret:
            return Response({"detail":"Otp Secret Not Found"},status=status.HTTP_404_NOT_FOUND)
        check_otp(serializer.validated_data['phone_number'],serializer.validated_data['otp_code'],otp_secret)
        try:
            user = User.objects.get(phone_number=serializer.validated_data['phone_number'])
            if user.is_verified:
                return Response({"detail":"Tasdiqlanmagan foydalanuvchi topilmadi!"},status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({"detail":"Invalid phone number!"},status=status.HTTP_400_BAD_REQUEST)
        user.is_verified=True
        user.is_active=True
        user.save()
        redis_conn.delete(f"{user.phone_number}:otp")
        redis_conn.delete(f"{user.phone_number}:otp_secret")

        UserServie.authenticate(user.phone_number,user.password)
        access = TokenService.get_valid_tokens(user.id,TokenType.ACCESS)
        refresh = TokenService.get_valid_tokens(user.id,TokenType.REFRESH)

        tokens = UserServie.create_tokens(user=user,access=str(access),refresh=str(refresh))
        TokenService.add_token_to_redis(user.id,tokens['access'],TokenType.ACCESS,expire_time=timedelta(days=2))
        TokenService.add_token_to_redis(user.id,tokens['refresh'],TokenType.REFRESH,expire_time=timedelta(days=3))
        return Response(tokens,status=status.HTTP_200_OK)

class LoginView(generics.CreateAPIView):
    serializer_class = LoginUserSerializer
    permission_classes = [AllowAny,]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = UserServie.authenticate(serializer.validated_data['email_or_phone_number'],serializer.validated_data['password'])
        except Exception as e:
            return Response({"detail":f"{e}"},status=status.HTTP_400_BAD_REQUEST)
        tokens = UserServie.create_tokens(user)
        return Response(tokens,status=status.HTTP_200_OK)

class UsersMeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [GeneratePermissions]

    def get_serializer_class(self):
        user = self.request.user
        group = user.groups.first()
        if group.name=='seller' and self.request.method=='GET':
            return SellerSerializer
        elif group.name=='buyer' and self.request.method=='GET':
            return BuyerSerializer
        return self.serializer_class

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        group = user.groups.first()
        if group.name=='seller':
            seller = SellerUser.objects.get(user=user)
        else:
            seller = BuyerUser.objects.get(user=user)
        serializer = self.get_serializer(seller)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user,data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)