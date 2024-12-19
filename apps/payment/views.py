from decouple import config, Choices
from django.shortcuts import render
import stripe
from rest_framework import status
from rest_framework.generics import UpdateAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import timedelta

from cart.models import Cart
from order.models import Order, StatusChoice
from order.permissions import CheckOrderUser
from payment.serializers import PaymentInitialSerializer, PaymentConfirmApiRequestSerializer
from share.services import ClientSecretService

stripe.api_key = config('STRIPE_TEST_SECRET_KEY')
# Create your views here.


class PaymentInitialApiView(APIView):
    serializer_class = PaymentInitialSerializer
    permission_classes = [IsAuthenticated,]
    def patch(self, request,id):
        order = get_object_or_404(Order,id=id)
        if order.status==StatusChoice.CANCELED:
            return Response(data={"detail":"Order already canceled."},status=status.HTTP_400_BAD_REQUEST)
        elif order.status==StatusChoice.DELIVERED:
            return Response(data={'detail':"Order has been delivered."},status=status.HTTP_400_BAD_REQUEST)
        elif order.status==StatusChoice.SHIPPED:
            return Response(data={'detail':'Order has been shipped.'},status=status.HTTP_400_BAD_REQUEST)
        elif order.status==StatusChoice.PAID:
            return Response(data={"detail":"Order is already paid."},status=status.HTTP_400_BAD_REQUEST)
        serializer = PaymentInitialSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"detail":"Card details are incomplete."},status=status.HTTP_400_BAD_REQUEST)
        card_number = serializer.validated_data.get('card_number')
        expiry_month = serializer.validated_data.get('expiry_month')
        expiry_year = serializer.validated_data.get('expiry_year')
        cvc = serializer.validated_data.get('cvc')

        try:
            intent = stripe.PaymentIntent.create(
                amount=int(order.amount*100),
                payment_method_data={
                    "type":"card",
                    "card":{
                        "number":card_number,
                        "exp_month":expiry_month,
                        "exp_year":expiry_year,
                        "cvc":cvc,
                    },
                },
                confirmation_method="manual",
                confirm=True,
            )
            order.transaction_id=intent['id']
            order.save()
            retrieve=stripe.PaymentIntent.retrieve(intent['id'])
            # ClientSecretService.add_client_secret_to_redis(user_id=request.user.id,client_secret=retrieve.get('client_secret'),lifetime=timedelta(minutes=30))
            return Response({"client_secret":retrieve.get('client_secret')},status=status.HTTP_200_OK)
        except stripe.error.CardError as e:
            return Response({"detail":str(e)},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": "Card details are incomplete."},
                            status=status.HTTP_400_BAD_REQUEST)


class PaymentConfirmApiView(APIView):
    serializer_class = PaymentConfirmApiRequestSerializer
    permission_classes = [IsAuthenticated,CheckOrderUser]
    def patch(self,request,id):
        order = get_object_or_404(Order,id=id)
        cart = get_object_or_404(Cart,user=request.user)
        if not order.status==StatusChoice.PENDING:
            return Response(data={"detail":"Order payment status cannot be updated."},status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        client_secret = serializer.validated_data.get('client_secret')
        # valid_client_secrets = ClientSecretService.get_valid_client_secret(user_id=request.user.id)
        # if not client_secret in valid_client_secrets:
        #     return Response(data={"detail":"secret token not correct"},status=status.HTTP_400_BAD_REQUEST)
        try:
            confirm = stripe.PaymentIntent.confirm(order.transaction_id)
            if confirm.get('status')=='succeeded':
                order.status=StatusChoice.PAID
                order.is_paid=True
                order.save()
                cart.items.all().delete()
                # ClientSecretService.delete_client_secret(user_id=request.user.id)
                return Response(data={"status":confirm.get('status')})
            return Response(data={"detail":"Order payment status cannot be updated."},status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.CardError as e:
            return Response(data={"error":str(e)},status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.InvalidRequestError as e:
            return Response(data={"error":str(e)},status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.StripeError as e:
            return Response(data={"error":str(e)},status=status.HTTP_400_BAD_REQUEST)


class PaymentCreateWithLinkApiView(APIView):
    permission_classes = [IsAuthenticated,CheckOrderUser]
    def patch(self,request,id):
        order = get_object_or_404(Order,id=id)
        if order.status==StatusChoice.CANCELED:
            return Response(data={"detail":"Order already canceled."},status=status.HTTP_400_BAD_REQUEST)
        elif order.status!=StatusChoice.PENDING:
            return Response(data={"detail":"Order cannot be updated."},status=status.HTTP_400_BAD_REQUEST)
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items = [{"price":order.amount,"quantity":sum([item.quantity for item in order.order_items.all()])}],
                mode="payment",
                success_url = request.build_absolute_uri('/api/payment/'+str(order.id) + '/success/'),
                cancel_url = request.build_absolute_uri('/api/payment/'+str(order.id)+'/cancel/')
            )
            order.transaction_id = checkout_session['id']
            order.save()
            return Response(data={"url":checkout_session['url']})
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)