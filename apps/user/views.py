from datetime import timedelta
from os import access
from secrets import token_urlsafe

from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.hashers import make_password

from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.translation import gettext as _
from rest_framework_simplejwt.tokens import RefreshToken

from share.enums import UserRole, TokenType
from share.permissions import GeneratePermissions
from share.services import TokenService
from share.utils import OTPService, check_otp
from user.models import BuyerUser, Group, SellerUser
from user.serializers import UserSerializer, VerifyCodeSerializer, LoginUserSerializer, \
    SellerSerializer, BuyerSerializer, ChangePasswordSerializer, \
    ForgotPasswordVerifyRequestSerializer, TokenResponseSerializer, ValidationErrorSerializer, \
    ForgotPasswordRequestSerializer, ForgotPasswordResponseSerializer, ForgotPasswordVerifyResponseSerializer, \
    ResetPasswordRequestSerializer
from share.utils import generate_otp,get_redis_conn
from rest_framework import generics

from user.services import UserServie
from user.tasks import send_email

User = get_user_model()

# Create your views here.
redis_conn = get_redis_conn()

@extend_schema_view(
    post=extend_schema(
        summary="Sign Up a user",
        request=UserSerializer,
        responses={
            201:UserSerializer,
            400:ValidationErrorSerializer
        }
    )
)
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
            return Response(data=data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

@extend_schema_view(
    patch=extend_schema(
        summary="Verify a user",
        request=VerifyCodeSerializer,
        responses={
            200:TokenResponseSerializer,
            400:ValidationErrorSerializer
        }
    )
)
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

        UserServie.authenticate(user.phone_number,user.password,quiet=True)
        access = TokenService.get_valid_tokens(user.id,TokenType.ACCESS)
        refresh = TokenService.get_valid_tokens(user.id,TokenType.REFRESH)

        tokens = UserServie.create_tokens(user=user,access=str(access),refresh=str(refresh))
        TokenService.add_token_to_redis(user.id,tokens['access'],TokenType.ACCESS,expire_time=timedelta(days=2))
        TokenService.add_token_to_redis(user.id,tokens['refresh'],TokenType.REFRESH,expire_time=timedelta(days=3))
        return Response(tokens,status=status.HTTP_200_OK)

@extend_schema_view(
    post = extend_schema(
        summary="Login a user",
        request=LoginUserSerializer,
        responses={
            200:TokenResponseSerializer,
            400:ValidationErrorSerializer
        }
    )
)
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

@extend_schema_view(
    get=extend_schema(
        summary="Get user information",
        responses={
            200:BuyerSerializer
        }
    ),
    patch=extend_schema(
        summary="Update user information",
        request=BuyerSerializer
    )
)


class UsersMeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    http_method_names = ['get','patch']
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        user = self.request.user
        group = user.groups.first()
        if group.name=='seller' and self.request.method=='GET':
                return SellerSerializer
        elif  group.name=='buyer' and self.request.method=='GET':
                return BuyerSerializer
        return self.serializer_class

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        print(user)
        group = user.groups.first()
        if group and group.name=='seller':
            seller = SellerUser.objects.get(user=user)
        elif group and group.name=='buyer':
            seller = BuyerUser.objects.get(user=user)
        else:
            return Response({'detail':'Error'},status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(seller)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user,data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@extend_schema_view(
    patch=extend_schema(
        summary="Update user information",
        request=ChangePasswordSerializer,
        responses={
            200:TokenResponseSerializer,
            400:ValidationErrorSerializer
        }
    )
)
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated,]
    serializer_class = ChangePasswordSerializer

    def put(self,request,*args,**kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = UserServie.authenticate(email_or_phone_number=request.user.phone_number,password=serializer.validated_data['old_password'])

        if user is not None:
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            tokens = UserServie.create_tokens(user)
            return Response(tokens)
        return Response(_("Eski Parol Xato!"))

@extend_schema_view(
    post=extend_schema(
        summary="Forgot Password to User",
        request=ForgotPasswordRequestSerializer,
        responses={
            200:ForgotPasswordResponseSerializer,
            400:ValidationErrorSerializer
        }
    )
)
class ForgotPasswordView(generics.CreateAPIView):
    serializer_class = ForgotPasswordRequestSerializer
    permission_classes = [AllowAny,]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        if redis_conn.exists(f"{email}:otp_secret"):
            secret_token = redis_conn.get(f"{email}:otp_secret")
        else:
            otp_code,secret_token = generate_otp(phone_number_or_email=email)
            send_email_status=send_email(email=email,otp_code=otp_code)
            print(send_email_status)
            if send_email_status==400:
                # redis_conn.delete(f"{email}:otp_secret")
                redis_conn.delete(f"{email}:otp")
                raise ValidationError({"detail":"Not Send Otp Code!"})
        data = {
            "email":email,
            "otp_secret":secret_token
        }

        return Response(data=data,status=status.HTTP_200_OK)

@extend_schema_view(
    post=extend_schema(
        summary="Forgot password verify a user",
        request=ForgotPasswordVerifyRequestSerializer,
        responses={
            200:ForgotPasswordVerifyResponseSerializer,
            400:ValidationErrorSerializer
        }
    )
)
class ForgotVerifyView(generics.CreateAPIView):
    serializer_class = ForgotPasswordVerifyRequestSerializer
    permission_classes = [AllowAny,]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp_secret = kwargs.get('otp_secret')
        email = serializer.validated_data['email']
        otp_code = serializer.validated_data['otp_code']
        users = User.objects.filter(email=email)
        if not users.exists():
            raise ValidationError("Active user not found!")

        check_otp(phone_number_or_email=email,otp_code=otp_code,otp_secret=otp_secret)
        redis_conn.delete(f'{email}:otp')
        token_hash = make_password(token_urlsafe())
        redis_conn.set(token_hash,email,ex=2*60*60)
        return Response({'token':token_hash},status=status.HTTP_200_OK)

@extend_schema_view(
    patch=extend_schema(
        summary="Reset password",
        request=ResetPasswordRequestSerializer,
        responses={
            200:TokenResponseSerializer,
            400:ValidationErrorSerializer
        }
    )
)
class ResetPasswordView(generics.UpdateAPIView):
    serializer_class = ResetPasswordRequestSerializer
    permission_classes = [AllowAny,]
    http_method_names = ['patch']

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token_hash = serializer.validated_data['token']
        email = redis_conn.get(token_hash)

        if not email:
            redis_conn.delete(token_hash)
            raise ValidationError("Token Yaroqsiz!")

        users = User.objects.filter(email=email.decode(),is_active=True)
        if not users.exists():
            redis_conn.delete(token_hash)
            return Response({"detail":"User not Found"},status=status.HTTP_404_NOT_FOUND)

        password = serializer.validated_data['password']
        user = users.first()
        user.set_password(password)
        user.save()

        update_session_auth_hash(request,user)
        tokens = UserServie.create_tokens(user=user)
        redis_conn.delete(token_hash)
        return Response(tokens,status=status.HTTP_200_OK)

@extend_schema_view(
    post=extend_schema(
        summary="Log out a user",
        request=None,
        responses={
            200:ValidationErrorSerializer,
            401:ValidationErrorSerializer
        }
    )
)
class LogOutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated,]
    @extend_schema(responses=None)
    def post(self, request, *args, **kwargs):
        UserServie.create_tokens(request.user,access='fake_token',refresh='fake_token',is_force_add_to_redis=True)
        return Response({'detail':"Muvafaqiyatli chiqildi!"})