from django.urls import path

from notification.views import NotificationListApiView, NotificationRetrieveUpdateApiView

urlpatterns = [
    path('',NotificationListApiView.as_view(),name='notification-list'),
    path('<uuid:pk>/',NotificationRetrieveUpdateApiView.as_view(),name='notification-retireve'),
]