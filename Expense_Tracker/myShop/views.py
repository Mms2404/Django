import json
from decimal import Decimal

from django.db import transaction
from rest_framework import viewsets, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from .models import Succulent, Pot, Order, OrderItem
from .serializers import (
    SucculentSerializer,
    PotSerializer,
    OrderCreateSerializer,
    OrderDetailSerializer,
    OrderStatusUpdateSerializer,
)
from . import razorpay_client


# --------------------------------------------------------------------------
# Catalog (public read)
# --------------------------------------------------------------------------

class SucculentViewSet(viewsets.ModelViewSet):
    queryset = Succulent.objects.all()
    serializer_class = SucculentSerializer
    permission_classes = [AllowAny]


class PotViewSet(viewsets.ModelViewSet):
    queryset = Pot.objects.all()
    serializer_class = PotSerializer
    permission_classes = [AllowAny]


# --------------------------------------------------------------------------
# Razorpay dashboard (browser)Sign up, get test keys. — Phase 1
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# Checkout — Phase 2
# --------------------------------------------------------------------------

class CheckoutView(APIView):
    """
    POST /api/shop/checkout/

    Public. Accepts cart + phone + address + payment_method from Flutter.

    Online flow:  Creates Order (status='pending')  → creates Razorpay order
                  → returns razorpay_order_id for Flutter to open payment UI.

    COD flow:     Creates Order (status='pending_cod') → returns order_id only.
                  No Razorpay involved. razorpay_order_id will be empty string.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data           = serializer.validated_data
        items          = data['items']
        payment_method = data.get('payment_method', 'online')

        # Server-side total. Never trust client.
        subtotal     = sum(Decimal(str(i['product_price'])) * i['quantity'] for i in items)
        delivery_fee = Decimal('20.00') if items else Decimal('0.00')
        total        = subtotal + delivery_fee

        if payment_method == 'cod':
            return self._handle_cod(data, items, total)
        else:
            return self._handle_online(data, items, total)
        
# --------------------------------------------------------------------------
# Payment verificationCustomer pays inside Razorpay's UI — Phase 3
# --------------------------------------------------------------------------


    # ------------------------------------------------------------------
    # COD — no Razorpay, order goes straight to pending_cod
    # ------------------------------------------------------------------
    def _handle_cod(self, data, items, total):
        try:
            with transaction.atomic():
                order = Order.objects.create(
                    phone          = data['phone'],
                    address        = data['address'],
                    latitude       = data.get('latitude'),
                    longitude      = data.get('longitude'),
                    total_amount   = total,
                    payment_method = 'cod',
                    status         = 'pending_cod',
                )
                for item in items:
                    OrderItem.objects.create(
                        order         = order,
                        product_name  = item['product_name'],
                        product_price = item['product_price'],
                        product_type  = item.get('product_type', 'succulent'),
                        quantity      = item['quantity'],
                    )
        except Exception as e:
            return Response(
                {'detail': f'Could not create order: {str(e)}'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {
                'order_id':          order.id,
                'razorpay_order_id': '',       # empty — Flutter ignores for COD
                'amount':            str(total),
                'currency':          'INR',
                'payment_method':    'cod',
            },
            status=status.HTTP_201_CREATED,
        )

    # ------------------------------------------------------------------
    # Online — create Razorpay order, return razorpay_order_id to Flutter
    # ------------------------------------------------------------------
    def _handle_online(self, data, items, total):
        try:
            with transaction.atomic():
                order = Order.objects.create(
                    phone          = data['phone'],
                    address        = data['address'],
                    latitude       = data.get('latitude'),
                    longitude      = data.get('longitude'),
                    total_amount   = total,
                    payment_method = 'online',
                    status         = 'pending',
                )
                for item in items:
                    OrderItem.objects.create(
                        order         = order,
                        product_name  = item['product_name'],
                        product_price = item['product_price'],
                        product_type  = item.get('product_type', 'succulent'),
                        quantity      = item['quantity'],
                    )

                razorpay_order_id = razorpay_client.create_order(
                    amount_rupees=total,
                    receipt=f'order_{order.id}',
                )
                order.razorpay_order_id = razorpay_order_id
                order.save(update_fields=['razorpay_order_id'])

        except Exception as e:
            return Response(
                {'detail': f'Could not create order: {str(e)}'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {
                'order_id':          order.id,
                'razorpay_order_id': razorpay_order_id,
                'amount':            str(total),
                'currency':          'INR',
                'payment_method':    'online',
            },
            status=status.HTTP_201_CREATED,
        )


# --------------------------------------------------------------------------
# Payment verification — Phase 4 (online only)
# --------------------------------------------------------------------------

class PaymentVerifyView(APIView):
    """
    POST /api/shop/payment/verify/

    Public. Called by Flutter after Razorpay returns success.
    Verifies HMAC signature. On success, marks order 'confirmed'.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        razorpay_order_id   = request.data.get('razorpay_order_id')
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_signature  = request.data.get('razorpay_signature')

        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return Response(
                {'detail': 'Missing payment fields.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        is_valid = razorpay_client.verify_payment_signature(
            razorpay_order_id, razorpay_payment_id, razorpay_signature
        )
        if not is_valid:
            return Response(
                {'detail': 'Signature verification failed.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
        except Order.DoesNotExist:
            return Response(
                {'detail': 'Order not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Only update if not already confirmed (e.g. webhook beat us to it).
        if order.status == 'pending':
            order.status     = 'confirmed'
            order.payment_id = razorpay_payment_id
            order.save(update_fields=['status', 'payment_id', 'updated_at'])

        return Response(OrderDetailSerializer(order).data, status=status.HTTP_200_OK)


# --------------------------------------------------------------------------
# Webhook — Phase 5 (online only, safety net)
# --------------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([AllowAny])
def razorpay_webhook(request):
    """
    POST /api/shop/razorpay/webhook/

    Razorpay calls this directly when payment.captured fires.
    Safety net: handles cases where Flutter crashed before calling /verify/.
    Authenticity is verified via Razorpay's HMAC webhook signature.

    To activate: go to Razorpay Dashboard → Settings → Webhooks,
    add this URL and set a webhook secret, then put that secret in
    settings.py as RAZORPAY_WEBHOOK_SECRET.
    """
    signature = request.headers.get('X-Razorpay-Signature', '')
    if not razorpay_client.verify_webhook_signature(request.body, signature):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    event = payload.get('event')
    if event == 'payment.captured':
        entity       = payload.get('payload', {}).get('payment', {}).get('entity', {})
        rp_order_id  = entity.get('order_id')
        rp_payment_id = entity.get('id')

        if rp_order_id and rp_payment_id:
            try:
                order = Order.objects.get(razorpay_order_id=rp_order_id)
                if order.status == 'pending':
                    order.status     = 'confirmed'
                    order.payment_id = rp_payment_id
                    order.save(update_fields=['status', 'payment_id', 'updated_at'])
            except Order.DoesNotExist:
                pass  # silently ignore unknown orders

    # Always return 200 — Razorpay retries on anything else.
    return Response(status=status.HTTP_200_OK)


# --------------------------------------------------------------------------
# Customer tracking (public, by phone)
# --------------------------------------------------------------------------

class CustomerOrdersView(generics.ListAPIView):
    """
    GET /api/shop/orders/?phone=9876543210

    Returns all orders for the given phone number, newest first.
    """
    serializer_class   = OrderDetailSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        phone = self.request.query_params.get('phone', '').strip()
        if not phone:
            return Order.objects.none()
        return Order.objects.filter(phone=phone)


# --------------------------------------------------------------------------
# Admin
# --------------------------------------------------------------------------

class AdminOrdersListView(generics.ListAPIView):
    """
    GET /api/shop/admin/orders/
    GET /api/shop/admin/orders/?status=pending_cod

    Admin only. Lists ALL orders. Optional status filter.
    """
    serializer_class   = OrderDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs            = Order.objects.all()
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs


class AdminOrderUpdateView(generics.UpdateAPIView):
    """
    PATCH /api/shop/admin/orders/<id>/

    Admin only. Updates the order status.
    """
    queryset           = Order.objects.all()
    serializer_class   = OrderStatusUpdateSerializer
    permission_classes = [IsAuthenticated]
    http_method_names  = ['patch']
