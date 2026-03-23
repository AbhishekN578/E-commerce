import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from orders.models import Order, OrderTracking
from payments.models import Payment, SellerPayout


class StripeWebhookView(APIView):
    """Handle Stripe webhook events."""
    permission_classes = [permissions.AllowAny]

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except (ValueError, stripe.error.SignatureVerificationError):
            return HttpResponse(status=400)

        event_type = event['type']

        if event_type == 'checkout.session.completed':
            self._handle_checkout_completed(event['data']['object'])
        elif event_type == 'payment_intent.payment_failed':
            self._handle_payment_failed(event['data']['object'])
        elif event_type == 'charge.refunded':
            self._handle_refund(event['data']['object'])

        return HttpResponse(status=200)

    def _handle_checkout_completed(self, session):
        order_id = session.get('metadata', {}).get('order_id')
        if not order_id:
            return
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return

        # Create or update payment record
        payment, _ = Payment.objects.update_or_create(
            order=order,
            defaults={
                'stripe_payment_intent_id': session.get('payment_intent', ''),
                'stripe_checkout_session_id': session.get('id', ''),
                'amount': order.total_amount,
                'status': 'succeeded',
            }
        )

        order.status = 'confirmed'
        order.save(update_fields=['status'])
        order.items.all().update(status='confirmed')

        OrderTracking.objects.create(
            order=order,
            status='confirmed',
            note='Payment received. Order confirmed.',
        )

        # Trigger payout to sellers
        self._create_seller_payouts(order)

    def _create_seller_payouts(self, order):
        """Transfer to each seller's Stripe Connect account."""
        stripe.api_key = settings.STRIPE_SECRET_KEY
        commission_pct = settings.PLATFORM_COMMISSION / 100

        from collections import defaultdict
        seller_totals = defaultdict(float)
        for item in order.items.select_related('seller').all():
            seller_totals[item.seller] += float(item.subtotal)

        for seller, amount in seller_totals.items():
            payout_amount = amount * (1 - commission_pct)
            commission = amount * commission_pct
            payout = SellerPayout.objects.create(
                seller=seller,
                order=order,
                amount=round(payout_amount, 2),
                commission_deducted=round(commission, 2),
                status='pending',
            )

            if seller.stripe_account_id and seller.stripe_onboarding_complete:
                try:
                    transfer = stripe.Transfer.create(
                        amount=int(payout_amount * 100),
                        currency='inr',
                        destination=seller.stripe_account_id,
                        metadata={'order_id': order.id, 'seller_id': seller.id},
                    )
                    payout.stripe_transfer_id = transfer.id
                    payout.status = 'paid'
                    payout.save()

                    # Update seller total_sales
                    seller.total_sales += payout_amount
                    seller.save(update_fields=['total_sales'])
                except stripe.error.StripeError:
                    payout.status = 'failed'
                    payout.save()

    def _handle_payment_failed(self, payment_intent):
        # Find order by payment_intent
        payment = Payment.objects.filter(stripe_payment_intent_id=payment_intent.get('id')).first()
        if payment:
            payment.status = 'failed'
            payment.save()
            payment.order.status = 'cancelled'
            payment.order.save(update_fields=['status'])

    def _handle_refund(self, charge):
        payment = Payment.objects.filter(stripe_payment_intent_id=charge.get('payment_intent')).first()
        if payment:
            payment.status = 'refunded'
            payment.save()
            payment.order.status = 'refunded'
            payment.order.save(update_fields=['status'])


class StripeConnectOnboardingView(APIView):
    """Generate Stripe Connect onboarding URL for seller."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        seller = request.user.seller_profile

        try:
            if not seller.stripe_account_id:
                account = stripe.Account.create(
                    type='express',
                    country='IN',
                    email=request.user.email,
                    capabilities={'transfers': {'requested': True}},
                )
                seller.stripe_account_id = account.id
                seller.save(update_fields=['stripe_account_id'])

            link = stripe.AccountLink.create(
                account=seller.stripe_account_id,
                refresh_url=f"{settings.FRONTEND_URL}/dashboard/seller/stripe/refresh/",
                return_url=f"{settings.FRONTEND_URL}/dashboard/seller/stripe/complete/",
                type='account_onboarding',
            )
            return Response({'onboarding_url': link.url})
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=400)


class StripeConnectStatusView(APIView):
    """Check and update seller's Stripe Connect onboarding status."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        seller = request.user.seller_profile

        if not seller.stripe_account_id:
            return Response({'connected': False, 'onboarding_complete': False})

        try:
            account = stripe.Account.retrieve(seller.stripe_account_id)
            details_submitted = account.get('details_submitted', False)
            if details_submitted and not seller.stripe_onboarding_complete:
                seller.stripe_onboarding_complete = True
                seller.save(update_fields=['stripe_onboarding_complete'])
            return Response({
                'connected': True,
                'onboarding_complete': details_submitted,
                'stripe_account_id': seller.stripe_account_id,
            })
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=400)
