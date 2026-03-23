from django.urls import path
from . import views

urlpatterns = [
    path('seller/analytics/', views.SellerAnalyticsView.as_view(), name='seller-analytics'),
    path('admin/analytics/', views.AdminPlatformAnalyticsView.as_view(), name='admin-analytics'),
]
