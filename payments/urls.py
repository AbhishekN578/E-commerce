from django.urls import path
from . import views

urlpatterns = [
    path('webhook/', views.StripeWebhookView.as_view(), name='stripe-webhook'),
    path('stripe/connect/', views.StripeConnectOnboardingView.as_view(), name='stripe-connect'),
    path('stripe/status/', views.StripeConnectStatusView.as_view(), name='stripe-status'),
]
