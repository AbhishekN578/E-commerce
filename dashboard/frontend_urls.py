from django.urls import path
from . import frontend_views

urlpatterns = [
    path('seller/register/', frontend_views.seller_register_view, name='seller-register'),
    path('seller/', frontend_views.seller_dashboard_view, name='seller-dashboard'),
]
