from django.urls import path
from .views import (
    CheckoutView,
    MyOrdersView,
    OrderDetailView,
    AdminOrderListView,
    UpdateOrderStatusView,
    CreateStripePaymentIntentView,
    RefundOrderView,
    RetryPaymentView,
    stripe_webhook,
)

urlpatterns = [
    # User Order Flow
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("my-orders/", MyOrdersView.as_view(), name="my-orders"),
    path("<uuid:order_id>/", OrderDetailView.as_view(), name="order-detail"),

    # Stripe Payment
    path("pay/<uuid:order_id>/", CreateStripePaymentIntentView.as_view(), name="create-payment-intent"),
    path("retry/<uuid:order_id>/", RetryPaymentView.as_view(), name="retry-payment"),
    path("webhook/", stripe_webhook, name="stripe-webhook"),

    # Admin
    path("admin/all/", AdminOrderListView.as_view(), name="admin-orders"),
    path("admin/update/<uuid:order_id>/", UpdateOrderStatusView.as_view(), name="update-order-status"),
    path("admin/refund/<uuid:order_id>/", RefundOrderView.as_view(), name="refund-order"),
]