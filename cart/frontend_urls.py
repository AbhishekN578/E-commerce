from django.urls import path
from . import frontend_views

urlpatterns = [
    path('', frontend_views.cart_view, name='cart-view'),
    path('add/<int:product_id>/', frontend_views.add_to_cart_view, name='cart-add'),
]
