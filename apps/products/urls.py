from django.urls import path
from .views import ProductListview,ProductDetailView
urlpatterns = [
    path("products/",ProductListview.as_view(),name='products-list'),
    path("products/<slug:slug>/",ProductDetailView.as_view(),name='product-detail')
]
