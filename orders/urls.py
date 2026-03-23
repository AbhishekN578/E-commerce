from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('', views.OrderListView.as_view(), name='order-list'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('seller/', views.SellerOrderListView.as_view(), name='seller-order-list'),
    path('admin/all/', views.AdminOrderListView.as_view(), name='admin-order-list'),
    path('items/<int:item_id>/status/', views.OrderItemStatusUpdateView.as_view(), name='order-item-status'),
]
