from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from .models import Product
from .serializers import ProductSerializer, ProductCreateUpdateSerializer
from apps.accounts.permissions import IsAdminUserRole
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination


class ProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    
    
class ProductListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):

        products = Product.objects.filter(is_active=True)

        # 🔎 Filter by category
        category = request.GET.get("category")
        if category:
            products = products.filter(category__iexact=category)

        # 🔎 Filter by gender
        gender = request.GET.get("gender")
        if gender:
            products = products.filter(gender__iexact=gender)

        # 🔎 Search
        search = request.GET.get("search")
        if search:
            products = products.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        # 🔎 Price range
        min_price = request.GET.get("min_price")
        max_price = request.GET.get("max_price")

        if min_price:
            products = products.filter(price__gte=min_price)

        if max_price:
            products = products.filter(price__lte=max_price)

        paginator = ProductPagination()
        result_page = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)
    
class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk, is_active=True)
        serializer = ProductSerializer(product)
        return Response(serializer.data)    
    
class ProductCreateView(APIView):
    permission_classes = [IsAdminUserRole]

    def post(self, request):
        serializer = ProductCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
    
    
class ProductUpdateView(APIView):
    permission_classes = [IsAdminUserRole]

    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductCreateUpdateSerializer(product, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProductDeleteView(APIView):
    permission_classes = [IsAdminUserRole]

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return Response({"message": "Product deleted successfully"}, status=204)        