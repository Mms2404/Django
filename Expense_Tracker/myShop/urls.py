from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SucculentViewSet,
    PotViewSet,
    CheckoutView,
    PaymentVerifyView,
    razorpay_webhook,
    CustomerOrdersView,
    AdminOrdersListView,
    AdminOrderUpdateView,
)


# Catalog uses a DRF router (auto-generates list/detail routes).
router = DefaultRouter()
router.register(r'succulents', SucculentViewSet)
router.register(r'pots', PotViewSet)


urlpatterns = [
    # Catalog — /api/shop/succulents/, /api/shop/pots/
    path('', include(router.urls)),

    # Checkout + payment — /api/shop/checkout/, /api/shop/payment/verify/
    path('checkout/', CheckoutView.as_view(), name='shop-checkout'),
    path('payment/verify/', PaymentVerifyView.as_view(), name='shop-payment-verify'),

    # Razorpay webhook — /api/shop/razorpay/webhook/
    path('razorpay/webhook/', razorpay_webhook, name='shop-razorpay-webhook'),

    # Customer tracking — /api/shop/orders/?phone=...
    path('orders/', CustomerOrdersView.as_view(), name='shop-customer-orders'),

    # Admin — /api/shop/admin/orders/, /api/shop/admin/orders/<id>/
    path('admin/orders/', AdminOrdersListView.as_view(), name='shop-admin-orders-list'),
    path('admin/orders/<int:pk>/', AdminOrderUpdateView.as_view(), name='shop-admin-order-update'),
]





# Webhook activation (one-time, when you deploy): 
# Go to Razorpay Dashboard → Settings → Webhooks → add your server URL https://yourserver.com/api/shop/razorpay/webhook/,
# tick the payment.captured event, set a secret, and put that secret in your settings.py as RAZORPAY_WEBHOOK_SECRET. 
# The view is already written — you're just telling Razorpay where to send it.