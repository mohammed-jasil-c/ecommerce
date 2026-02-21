from django.urls import path
from .views import (
    ProductListView,
    ProductDetailView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
)

urlpatterns = [
    path("", ProductListView.as_view()),
    path("<uuid:pk>/", ProductDetailView.as_view()),
    path("create/", ProductCreateView.as_view()),
    path("<uuid:pk>/update/", ProductUpdateView.as_view()),
    path("<uuid:pk>/delete/", ProductDeleteView.as_view()),
]