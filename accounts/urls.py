from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', views.MeView.as_view(), name='me'),
    path('seller/profile/', views.SellerProfileView.as_view(), name='seller-profile'),
    path('seller/create/', views.CreateSellerProfileView.as_view(), name='seller-create'),
    path('buyer/profile/', views.BuyerProfileView.as_view(), name='buyer-profile'),
    path('admin/sellers/', views.SellerListView.as_view(), name='seller-list'),
    path('admin/sellers/<int:seller_id>/approval/', views.SellerApprovalView.as_view(), name='seller-approval'),
]
