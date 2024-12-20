from django.urls import path

from notification.views import NotificationListApiView

urlpatterns = [
    path('',NotificationListApiView.as_view(),name='notification-list'),
]