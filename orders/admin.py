from django.contrib import admin
from .models import Order, OrderItem, OrderTracking

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'seller', 'product_name', 'product_price', 'quantity', 'subtotal')


class OrderTrackingInline(admin.TabularInline):
    model = OrderTracking
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'buyer', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('buyer__email', 'shipping_name')
    readonly_fields = ('total_amount', 'platform_commission')
    inlines = [OrderItemInline, OrderTrackingInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'seller', 'quantity', 'status')
    list_filter = ('status', 'seller')
    search_fields = ('order__id', 'product_name', 'seller__business_name')
