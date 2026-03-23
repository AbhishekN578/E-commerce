from django.urls import path
from . import frontend_views

urlpatterns = [
    path('login/', frontend_views.login_view, name='frontend-login'),
    path('register/', frontend_views.register_view, name='frontend-register'),
    path('logout/', frontend_views.logout_view, name='frontend-logout'),
    path('profile/', frontend_views.profile_view, name='frontend-profile'),
]
