from django.urls import path
from products import frontend_views

urlpatterns = [
    path('', frontend_views.HomeView.as_view(), name='home'),
    path('products/', frontend_views.product_list_view, name='product-list'),
    path('products/<slug:slug>/', frontend_views.product_detail_view, name='product-detail'),
    path('api/products/html/', frontend_views.featured_products_htmx, name='featured-products-html'),
]
