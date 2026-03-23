from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Order, OrderItem, OrderTracking
from .serializers import OrderSerializer, CheckoutSerializer, OrderItemStatusSerializer
from cart.models import Cart
from cart.views import get_or_create_cart
from accounts.permissions import IsAdmin


class CheckoutView(APIView):
    """Create order from cart and initiate Stripe Checkout."""
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        cart = get_or_create_cart(request)
        if not cart.items.exists():
            return Response({'error': 'Your cart is empty.'}, status=400)

        # Calculate totals
        total = cart.total
        commission_pct = settings.PLATFORM_COMMISSION / 100
        commission = round(total * commission_pct, 2)

        # Create order
        order = Order.objects.create(
            buyer=request.user,
            total_amount=total,
            platform_commission=commission,
            **data,
        )

        # Create order items (split by seller)
        for cart_item in cart.items.select_related('product__seller').all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                seller=cart_item.product.seller,
                product_name=cart_item.product.name,
                product_price=cart_item.product.effective_price,
                quantity=cart_item.quantity,
            )
            # Reduce stock
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save(update_fields=['stock'])

        # Add initial tracking
        OrderTracking.objects.create(order=order, status='pending', note='Order placed.', created_by=request.user)

        # Create Stripe Checkout session
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            line_items = []
            for item in order.items.select_related('product').all():
                line_items.append({
                    'price_data': {
                        'currency': 'inr',
                        'product_data': {'name': item.product_name},
                        'unit_amount': int(item.product_price * 100),
                    },
                    'quantity': item.quantity,
                })

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=f"{settings.FRONTEND_URL}/orders/{order.id}/success/",
                cancel_url=f"{settings.FRONTEND_URL}/cart/",
                metadata={'order_id': order.id},
            )

            # Clear cart
            cart.items.all().delete()

            return Response({
                'order': OrderSerializer(order).data,
                'checkout_url': session.url,
                'session_id': session.id,
            }, status=status.HTTP_201_CREATED)

        except stripe.error.StripeError as e:
            # Rollback order on stripe failure
            order.delete()
            return Response({'error': str(e)}, status=400)


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user).prefetch_related('items', 'tracking_history')


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Order.objects.all()
        return Order.objects.filter(buyer=self.request.user)


class SellerOrderListView(generics.ListAPIView):
    """Orders that contain the seller's products."""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        seller = self.request.user.seller_profile
        order_ids = OrderItem.objects.filter(seller=seller).values_list('order_id', flat=True).distinct()
        return Order.objects.filter(id__in=order_ids).prefetch_related('items', 'tracking_history')


class OrderItemStatusUpdateView(APIView):
    """Seller updates item status (shipped, delivered)."""
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, item_id):
        item = get_object_or_404(OrderItem, id=item_id, seller=request.user.seller_profile)
        serializer = OrderItemStatusSerializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Add tracking note
        tracking_note = f"Item '{item.product_name}' status updated to {item.status}."
        OrderTracking.objects.create(
            order=item.order,
            status=item.status,
            note=tracking_note,
            created_by=request.user,
        )

        # Check if all items completed → update order status
        order = item.order
        all_statuses = list(order.items.values_list('status', flat=True))
        if all(s == 'delivered' for s in all_statuses):
            order.status = 'delivered'
            order.save(update_fields=['status'])
        elif any(s == 'shipped' for s in all_statuses):
            order.status = 'shipped'
            order.save(update_fields=['status'])

        return Response(OrderSerializer(order).data)


class AdminOrderListView(generics.ListAPIView):
    """Admin: all orders."""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return Order.objects.all().prefetch_related('items', 'tracking_history').select_related('buyer')
