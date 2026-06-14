from rest_framework import serializers
from .models import Succulent, Pot, Order, OrderItem


# --------------------------------------------------------------------------
# Catalog
# --------------------------------------------------------------------------

class SucculentSerializer(serializers.ModelSerializer):
    image_path = serializers.SerializerMethodField()

    class Meta:
        model = Succulent
        fields = ['id', 'name', 'price', 'description', 'image_path']

    def get_image_path(self, obj):
        return self.context['request'].build_absolute_uri(obj.image.url)


class PotSerializer(serializers.ModelSerializer):
    image_path = serializers.SerializerMethodField()

    class Meta:
        model = Pot
        fields = ['id', 'name', 'material', 'height', 'width',
                  'price', 'description', 'image_path']

    def get_image_path(self, obj):
        return self.context['request'].build_absolute_uri(obj.image.url)


# --------------------------------------------------------------------------
# Orders
# --------------------------------------------------------------------------

class OrderItemInputSerializer(serializers.Serializer):
    """Each cart line coming from Flutter at checkout."""
    product_name  = serializers.CharField(max_length=100)
    product_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    product_type  = serializers.ChoiceField(choices=OrderItem.PRODUCT_TYPE_CHOICES)
    quantity      = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    """Incoming checkout payload from Flutter."""
    phone          = serializers.CharField(max_length=15)
    address        = serializers.CharField()
    latitude       = serializers.FloatField(required=False, allow_null=True)
    longitude      = serializers.FloatField(required=False, allow_null=True)
    # NEW — 'online' or 'cod'. Defaults to 'online' so old clients still work.
    payment_method = serializers.ChoiceField(
        choices=['online', 'cod'],
        default='online',
    )
    items = OrderItemInputSerializer(many=True)

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError('Cart cannot be empty.')
        return items


class OrderItemOutputSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'product_price', 'product_type',
                  'quantity', 'line_total']


class OrderDetailSerializer(serializers.ModelSerializer):
    """Order with its items — used in tracking + admin list responses."""
    items = OrderItemOutputSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'phone', 'address', 'latitude', 'longitude',
                  'total_amount', 'payment_method', 'razorpay_order_id',
                  'payment_id', 'status', 'created_at', 'updated_at', 'items']


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """Admin PATCHes only the status."""
    class Meta:
        model  = Order
        fields = ['status']
