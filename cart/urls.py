from django.urls import path
from . import views

urlpatterns = [
    path('', views.CartView.as_view(), name='cart'),
    path('add/', views.CartAddView.as_view(), name='cart-add'),
    path('clear/', views.CartClearView.as_view(), name='cart-clear'),
    path('item/<int:item_id>/', views.CartUpdateView.as_view(), name='cart-item'),
    path('wishlist/', views.WishlistView.as_view(), name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.WishlistToggleView.as_view(), name='wishlist-toggle'),
]
