from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from notification.models import Notification
from notification.serializers import NotificationSerializer
from share.permissions import GeneratePermissions


# Create your views here.

class NotificationListApiView(GeneratePermissions,ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
