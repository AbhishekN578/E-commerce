from django.shortcuts import render
from django.views.generic import TemplateView
from products.models import Product

class HomeView(TemplateView):
    template_name = 'home.html'

def product_list_view(request):
    products = Product.objects.filter(status='active').select_related('seller')
    
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
        
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(name__icontains=search_query)
        
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
        
    return render(request, 'products/list.html', {'products': products})

from django.shortcuts import get_object_or_404

def product_detail_view(request, slug):
    product = get_object_or_404(Product.objects.select_related('seller', 'category').prefetch_related('images'), slug=slug, status='active')
    
    # Simple view count increment
    product.view_count += 1
    product.save(update_fields=['view_count'])
    
    return render(request, 'products/detail.html', {'product': product})

def featured_products_htmx(request):
    """Returns HTML partial of featured products for the homepage."""
    products = Product.objects.filter(status='active', is_featured=True).select_related('seller', 'category')[:5]
    return render(request, 'products/partials/product_cards.html', {'products': products})
