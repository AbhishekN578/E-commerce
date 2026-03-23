from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('', views.ProductListView.as_view(), name='product-list'),
    path('my/', views.SellerProductListView.as_view(), name='seller-product-list'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('<slug:slug>/images/', views.ProductImageUploadView.as_view(), name='product-image-upload'),
    path('<slug:slug>/reviews/', views.ReviewListView.as_view(), name='review-list'),
    path('<slug:slug>/reviews/add/', views.ReviewCreateView.as_view(), name='review-create'),
]
