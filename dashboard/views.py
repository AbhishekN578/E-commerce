from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from products.models import Product
from orders.models import OrderItem, Order
from accounts.models import SellerProfile
from accounts.permissions import IsSeller, IsAdmin


class SellerAnalyticsView(APIView):
    """Analytics for a specific seller's dashboard."""
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get(self, request):
        seller = request.user.seller_profile
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)

        # Revenue
        total_revenue = OrderItem.objects.filter(
            seller=seller, status__in=['confirmed', 'shipped', 'delivered']
        ).aggregate(total=Sum('product_price'))['total'] or 0

        recent_revenue = OrderItem.objects.filter(
            seller=seller, status__in=['confirmed', 'shipped', 'delivered'],
            order__created_at__gte=thirty_days_ago
        ).aggregate(total=Sum('product_price'))['total'] or 0

        # Orders
        total_orders = OrderItem.objects.filter(seller=seller).values('order_id').distinct().count()
        pending_orders = OrderItem.objects.filter(seller=seller, status='pending').count()

        # Products
        active_products = Product.objects.filter(seller=seller, status='active').count()
        low_stock_products = Product.objects.filter(seller=seller, stock__lte=5, status='active').count()

        return Response({
            'total_revenue': float(total_revenue),
            'revenue_last_30_days': float(recent_revenue),
            'total_orders': total_orders,
            'pending_order_items': pending_orders,
            'active_products': active_products,
            'low_stock_products': low_stock_products,
        })


class AdminPlatformAnalyticsView(APIView):
    """Overall platform analytics for superadmin."""
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get(self, request):
        # Revenue
        total_sales = Order.objects.filter(status__in=['confirmed', 'shipped', 'delivered']).aggregate(
            total=Sum('total_amount'), commission=Sum('platform_commission')
        )
        platform_revenue = total_sales['commission'] or 0
        gross_volume = total_sales['total'] or 0

        # Users
        sellers_count = SellerProfile.objects.count()
        pending_sellers = SellerProfile.objects.filter(is_approved=False).count()

        # Orders
        total_orders = Order.objects.count()

        return Response({
            'gross_merchandise_volume': float(gross_volume),
            'platform_net_revenue': float(platform_revenue),
            'total_sellers': sellers_count,
            'pending_seller_approvals': pending_sellers,
            'total_orders': total_orders,
        })
