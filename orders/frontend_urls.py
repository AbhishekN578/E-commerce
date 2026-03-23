from django.urls import path
from . import frontend_views

urlpatterns = [
    path('checkout/', frontend_views.checkout_view, name='checkout-view'),
    path('orders/', frontend_views.order_list_view, name='order-list-view'),
    path('orders/<int:order_id>/', frontend_views.order_detail_view, name='order-detail-view'),
]
