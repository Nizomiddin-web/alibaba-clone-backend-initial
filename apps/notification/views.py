from django.shortcuts import render
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated

from notification.models import Notification
from notification.permissions import IsOwner
from notification.serializers import NotificationSerializer, NotificationUpdateRequestSerializer
from share.permissions import GeneratePermissions


# Create your views here.

class NotificationListApiView(GeneratePermissions,ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

class NotificationRetrieveUpdateApiView(GeneratePermissions,RetrieveUpdateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated,IsOwner]
    http_method_names = ['get','patch']

    def get_serializer_class(self):
        if self.request.method=='PATCH':
            return NotificationUpdateRequestSerializer
        return super().get_serializer_class()