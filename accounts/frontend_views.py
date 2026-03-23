from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .serializers import RegisterSerializer, SellerProfileSerializer, BuyerProfileSerializer
from .models import SellerProfile, BuyerProfile

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            return render(request, 'accounts/login.html', {'error': 'Invalid email or password.'})
    return render(request, 'accounts/login.html')

def register_view(request):
    if request.method == 'POST':
        # Simple frontend register mapping to the serializer
        data = request.POST.dict()
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'accounts/register.html', {'errors': serializer.errors})
    return render(request, 'accounts/register.html')

def logout_view(request):
    logout(request)
    return redirect('/')

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')
