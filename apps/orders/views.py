from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import stripe

from apps.cart.models import Cart
from apps.products.models import ProductVariant
from apps.accounts.permissions import IsAdminUserRole
from .models import Order, OrderItem, Payment
from .serializers import OrderSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):

        cart = Cart.objects.filter(user=request.user).first()

        if not cart or not cart.items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        total_amount = 0

        # Validate stock (NO deduction)
        for item in cart.items.all():
            if item.variant.stock < item.quantity:
                return Response(
                    {"error": f"Not enough stock for {item.variant.product.name}"},
                    status=400
                )

        order = Order.objects.create(
            user=request.user,
            status="pending_payment",
            payment_status="pending",
            total_amount=0
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                variant=item.variant,
                price=item.variant.product.price,
                quantity=item.quantity
            )

            total_amount += item.variant.product.price * item.quantity

        order.total_amount = total_amount
        order.save()

        payment = Payment.objects.create(
            order=order,
            amount=total_amount,
            status="pending"
        )

        return Response({
            "message": "Order created, proceed to payment",
            "order_id": order.id,
            "payment_id": payment.id,
            "amount": total_amount
        }) 
        
class MyOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
class UpdateOrderStatusView(APIView):
    permission_classes = [IsAdminUserRole]

    def put(self, request, order_id):

        order = get_object_or_404(Order, id=order_id)

        new_status = request.data.get("status")

        allowed_statuses = dict(Order.STATUS_CHOICES).keys()

        if new_status not in allowed_statuses:
            return Response({"error": "Invalid status"}, status=400)

        # Prevent invalid transitions
        if order.status in ["refunded", "cancelled"]:
            return Response({"error": "Cannot modify this order"}, status=400)

        order.status = new_status
        order.save()

        return Response({"message": "Order status updated"})                    
        
class CreateStripePaymentIntentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):

        order = get_object_or_404(
            Order,
            id=order_id,
            user=request.user
        )

        if order.payment_status != "pending":
            return Response({"error": "Payment already processed"}, status=400)

        intent = stripe.PaymentIntent.create(
            amount=int(order.total_amount * 100),
            currency="inr",
            metadata={
                "order_id": str(order.id),
                "user_id": str(request.user.id)
            }
        )

        order.payment.transaction_id = intent.id
        order.payment.save()

        return Response({"client_secret": intent.client_secret})
    
    
@csrf_exempt
def stripe_webhook(request):

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception:
        return HttpResponse(status=400)

    if event["type"] == "payment_intent.succeeded":

        intent = event["data"]["object"]
        order_id = intent["metadata"]["order_id"]

        order = Order.objects.get(id=order_id)

        # Idempotency protection
        if order.payment_status == "paid":
            return HttpResponse(status=200)

        # Update payment
        order.payment.status = "succeeded"
        order.payment.save()

        order.status = "confirmed"
        order.payment_status = "paid"
        order.save()

        # Deduct stock safely
        for item in order.items.all():
            variant = item.variant
            variant.stock -= item.quantity
            variant.save()

        # Clear cart
        cart = Cart.objects.filter(user=order.user).first()
        if cart:
            cart.items.all().delete()

    if event["type"] == "payment_intent.payment_failed":

        intent = event["data"]["object"]
        order_id = intent["metadata"]["order_id"]

        order = Order.objects.get(id=order_id)

        order.payment.status = "failed"
        order.payment.save()

        order.status = "cancelled"
        order.payment_status = "failed"
        order.save()

    return HttpResponse(status=200)


class RetryPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):

        order = get_object_or_404(
            Order,
            id=order_id,
            user=request.user
        )

        if order.payment_status != "failed":
            return Response({"error": "Retry not allowed"}, status=400)

        intent = stripe.PaymentIntent.create(
            amount=int(order.total_amount * 100),
            currency="inr",
            metadata={
                "order_id": str(order.id),
                "user_id": str(request.user.id)
            }
        )

        order.payment.transaction_id = intent.id
        order.payment.status = "pending"
        order.payment.save()

        order.status = "pending_payment"
        order.save()

        return Response({"client_secret": intent.client_secret})
    
    
    
class RefundOrderView(APIView):
    permission_classes = [IsAdminUserRole]

    @transaction.atomic
    def post(self, request, order_id):

        order = get_object_or_404(Order, id=order_id)

        if order.payment_status != "paid":
            return Response({"error": "Refund not allowed"}, status=400)

        stripe.Refund.create(
            payment_intent=order.payment.transaction_id
        )

        order.payment.status = "refunded"
        order.payment.save()

        order.status = "refunded"
        order.payment_status = "refunded"
        order.save()

        # Restore stock
        for item in order.items.all():
            variant = item.variant
            variant.stock += item.quantity
            variant.save()

        return Response({"message": "Refund successful"})
    
    
    
    
    
    class MyOrdersView(APIView):
        
     permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(
            Order,
            id=order_id,
            user=request.user
        )
        serializer = OrderSerializer(order)
        return Response(serializer.data)


class AdminOrderListView(APIView):
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        orders = Order.objects.all().order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)                