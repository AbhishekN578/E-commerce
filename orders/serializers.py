from rest_framework import serializers
from .models import Order, OrderItem, OrderTracking
from products.serializers import ProductListSerializer


class OrderTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderTracking
        fields = ['id', 'status', 'note', 'timestamp']


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'status', 'subtotal', 'seller']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    tracking_history = OrderTrackingSerializer(many=True, read_only=True)
    order_number = serializers.ReadOnlyField()
    buyer_email = serializers.CharField(source='buyer.email', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'buyer_email', 'status', 'total_amount',
            'shipping_name', 'shipping_email', 'shipping_phone',
            'shipping_address', 'shipping_city', 'shipping_state',
            'shipping_postal_code', 'shipping_country',
            'notes', 'items', 'tracking_history', 'created_at',
        ]
        read_only_fields = ['status', 'total_amount', 'created_at']


class CheckoutSerializer(serializers.Serializer):
    shipping_name = serializers.CharField(max_length=200)
    shipping_email = serializers.EmailField()
    shipping_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    shipping_address = serializers.CharField()
    shipping_city = serializers.CharField(max_length=100)
    shipping_state = serializers.CharField(max_length=100)
    shipping_postal_code = serializers.CharField(max_length=20)
    shipping_country = serializers.CharField(max_length=100, default='India')
    notes = serializers.CharField(required=False, allow_blank=True)


class OrderItemStatusSerializer(serializers.ModelSerializer):
    """For sellers to update their item status."""
    class Meta:
        model = OrderItem
        fields = ['status']
