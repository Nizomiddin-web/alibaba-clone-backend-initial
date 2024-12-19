from decouple import config
from django.shortcuts import render
import stripe
from rest_framework import status
from rest_framework.generics import UpdateAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from order.models import Order, StatusChoice
from payment.serializers import PaymentInitialSerializer

stripe.api_key = config('STRIPE_TEST_SECRET_KEY')
# Create your views here.


class PaymentInitialApiView(APIView):
    serializer_class = PaymentInitialSerializer
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
            retrieve=stripe.PaymentIntent.retrieve(intent['id'])
            return Response({"client_secret":retrieve.get('client_secret')},status=status.HTTP_200_OK)
        except stripe.error.CardError as e:
            return Response({"detail":str(e)},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": "Card details are incomplete."},
                            status=status.HTTP_400_BAD_REQUEST)

