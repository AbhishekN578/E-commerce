from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db import transaction
from cart.models import Cart
from .models import Order, OrderItem, OrderTracking
from django.contrib import messages
import stripe

@login_required
def checkout_view(request):
    try:
        cart = Cart.objects.get(user=request.user)
        if not cart.items.exists():
            return redirect('/cart/')
    except Cart.DoesNotExist:
        return redirect('/cart/')
        
    if request.method == 'POST':
        # Simple checkout logic for frontend
        shipping_address = request.POST.get('shipping_address', 'Default Address')
        phone_number = request.POST.get('phone_number', '0000000000')
        
        total = cart.total_amount
        commission_pct = settings.PLATFORM_COMMISSION / 100
        commission = round(total * commission_pct, 2)
        
        with transaction.atomic():
            order = Order.objects.create(
                buyer=request.user,
                total_amount=total,
                platform_commission=commission,
                shipping_address=shipping_address,
                phone_number=phone_number,
            )
            
            for cart_item in cart.items.select_related('product__seller').all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    seller=cart_item.product.seller,
                    product_name=cart_item.product.name,
                    product_price=cart_item.product.effective_price,
                    quantity=cart_item.quantity,
                )
                cart_item.product.stock -= cart_item.quantity
                cart_item.product.save(update_fields=['stock'])
            
            OrderTracking.objects.create(order=order, status='pending', note='Order placed.', created_by=request.user)
            
            # Stripe checkout
            stripe.api_key = settings.STRIPE_SECRET_KEY
            if not stripe.api_key:
                # If no stripe key in env, just clear cart and return to order list (Dummy mode)
                cart.items.all().delete()
                messages.success(request, 'Order placed successfully (Test Mode).')
                return redirect(f'/orders/{order.id}/')
                
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
                    success_url=f"{settings.FRONTEND_URL}/orders/",
                    cancel_url=f"{settings.FRONTEND_URL}/cart/",
                    metadata={'order_id': order.id},
                )
                
                cart.items.all().delete()
                return redirect(session.url)
            except Exception as e:
                order.delete()
                messages.error(request, f'Payment error: {str(e)}')
                return redirect('/cart/')
                
    context = {
        'cart': cart,
        'items': cart.items.select_related('product', 'product__seller')
    }
    return render(request, 'checkout/checkout.html', context)

@login_required
def order_list_view(request):
    orders = Order.objects.filter(buyer=request.user).order_by('-created_at').prefetch_related('items', 'items__product')
    return render(request, 'orders/order_list.html', {'orders': orders})

@login_required
def order_detail_view(request, order_id):
    order = Order.objects.prefetch_related('items', 'items__product', 'items__seller', 'tracking_history').get(id=order_id, buyer=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})
