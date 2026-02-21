from django.urls import path
from .views import (
    MyCartView,
    AddToCartView,
    UpdateCartItemView,
    RemoveCartItemView,
    ClearCartView,
)

urlpatterns = [
    path("", MyCartView.as_view()),
    path("add/", AddToCartView.as_view()),
    path("update/<uuid:item_id>/", UpdateCartItemView.as_view()),
    path("remove/<uuid:item_id>/", RemoveCartItemView.as_view()),
    path("clear/", ClearCartView.as_view()),
]