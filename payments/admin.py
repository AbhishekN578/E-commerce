from django.contrib import admin
from .models import Payment, SellerPayout


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'stripe_payment_intent_id', 'amount', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('stripe_payment_intent_id', 'order__id')
    readonly_fields = ('order', 'stripe_payment_intent_id', 'stripe_checkout_session_id', 'amount', 'currency')


@admin.register(SellerPayout)
class SellerPayoutAdmin(admin.ModelAdmin):
    list_display = ('seller', 'order', 'amount', 'status', 'created_at')
    list_filter = ('status', 'seller')
    search_fields = ('stripe_transfer_id', 'seller__business_name')
    readonly_fields = ('seller', 'order', 'amount', 'commission_deducted')
