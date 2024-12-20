from django.urls import path

from wishlist.views import WishListCreateApiView

urlpatterns = [
    path('',WishListCreateApiView.as_view(),name='wishlist-create-list')
]