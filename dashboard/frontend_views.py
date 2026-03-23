from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import SellerProfile
from products.models import Product
from orders.models import OrderItem
from django.db.models import Sum

def seller_register_view(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('/accounts/login/?next=/dashboard/seller/register/')
            
        business_name = request.POST.get('business_name')
        phone = request.POST.get('phone')
        
        # Update user role
        request.user.role = 'seller'
        request.user.save()
        
        # Create profile
        SellerProfile.objects.create(
            user=request.user,
            business_name=business_name,
            phone=phone
        )
        # In a real app, this waits for admin approval. Let's redirect to dashboard which will show pending status
        return redirect('/dashboard/seller/')
        
    return render(request, 'dashboard/seller_register.html')

@login_required
def seller_dashboard_view(request):
    if request.user.role != 'seller':
        return redirect('/')
        
    try:
        profile = request.user.seller_profile
    except SellerProfile.DoesNotExist:
        return redirect('/dashboard/seller/register/')
        
    context = {
        'profile': profile,
        'active_products': Product.objects.filter(seller=profile, status='active').count(),
        'pending_orders': OrderItem.objects.filter(seller=profile, status='pending').count(),
        'recent_orders': OrderItem.objects.filter(seller=profile).select_related('order', 'product')[:5]
    }
    
    return render(request, 'dashboard/seller_dashboard.html', context)
