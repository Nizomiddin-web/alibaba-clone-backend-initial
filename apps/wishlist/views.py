from django.shortcuts import render
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from order.permissions import CheckOrderUser
from share.pagination import CustomPagination
from share.permissions import GeneratePermissions
from wishlist.models import Wishlist
from wishlist.serializers import WishlistSerializer


# Create your views here.


class WishListCreateApiView(GeneratePermissions,ListAPIView,CreateAPIView):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated,CheckOrderUser]
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class WishlistRetrieveDestroyApiView(GeneratePermissions,RetrieveDestroyAPIView):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = {IsAuthenticated,CheckOrderUser}