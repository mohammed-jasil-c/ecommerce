from django.contrib import admin
from .models import Order, OrderItem, ShippingAddress, Payment
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(Payment)
# Register your models here.
