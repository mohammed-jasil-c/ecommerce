from django.urls import path
from .views import AddToWishlistView, MyWishlistView, RemoveFromWishlistView

urlpatterns = [
    path("add/", AddToWishlistView.as_view()),
    path("view/", MyWishlistView.as_view()),
    path("remove/<uuid:wishlist_id>/", RemoveFromWishlistView.as_view()),
]