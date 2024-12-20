from django.urls import path

from wishlist.views import WishListCreateApiView, WishlistRetrieveDestroyApiView

urlpatterns = [
    path('',WishListCreateApiView.as_view(),name='wishlist-create-list'),
    path('<uuid:pk>/',WishlistRetrieveDestroyApiView.as_view(),name='wishlist-create-list'),
]