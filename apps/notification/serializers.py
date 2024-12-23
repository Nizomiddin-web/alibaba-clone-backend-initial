from rest_framework import serializers

from notification.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id','user','type','message','is_read','created_at']
        read_only_fields = ['created_at']

class NotificationUpdateRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['is_read']