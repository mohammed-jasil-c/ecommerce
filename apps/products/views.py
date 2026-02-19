# from django.shortcuts import get_object_or_404
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from .models import Product
# from .serializers import ProductSerializer
# from rest_framework import status
# from .permissions import isAdminReadOnly



# class ProductListview(APIView):
#     permission_classes = [isAdminReadOnly]
    
#     def get(self,request):
#         products = Product.objects.filter(is_active=True)
#         serializer = ProductSerializer(products , many=True,)
#         return Response(serializer.data , status=status.HTTP_200_OK)
    
#     def post(self,request):
#         serializer = ProductSerializer(data =request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

# class ProductDetailView(APIView):
#     permission_classes = [isAdminReadOnly]
    
#     def get_object(self,slug):
#         return get_object_or_404(Product,slug=slug,is_active=True)
        
#     def get(self,request,slug):
#         product = self.get_object(slug)
#         serializer = ProductSerializer(product)
#         return Response(serializer.data , status=status.HTTP_200_OK)
    
#     def put(self,request,slug):
#         product = self.get_object(slug)
#         serializer = ProductSerializer(product , data = request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)
    
#     def patch(self,request,slug):
#         product = self.get_object(slug)
#         serializer = ProductSerializer(product,request.data,partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors ,status=status.HTTP_400_BAD_REQUEST)
    
#     def delete(self,request,slug):
#         product = self.get_object(slug) 
#         product.is_active = False
#         product.save()
#         return Response({"message":"product deleted successfully"},status=status.HTTP_204_NO_CONTENT)