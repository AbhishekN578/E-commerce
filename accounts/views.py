from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import CustomUser, SellerProfile, BuyerProfile
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    SellerProfileSerializer, CreateSellerProfileSerializer, BuyerProfileSerializer
)
from .permissions import IsSeller, IsAdmin


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'message': 'Registration successful.',
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return Response({
            'user': UserSerializer(data['user']).data,
            'access': data['access'],
            'refresh': data['refresh'],
        })


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully.'})
        except Exception:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class SellerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = SellerProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_object(self):
        return self.request.user.seller_profile


class CreateSellerProfileView(generics.CreateAPIView):
    serializer_class = CreateSellerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        user.role = 'seller'
        user.save()
        serializer.save()


class BuyerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = BuyerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = BuyerProfile.objects.get_or_create(user=self.request.user)
        return profile


class SellerApprovalView(APIView):
    """Admin only — approve or reject a seller."""
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def patch(self, request, seller_id):
        try:
            profile = SellerProfile.objects.get(id=seller_id)
        except SellerProfile.DoesNotExist:
            return Response({'error': 'Seller not found.'}, status=404)
        action = request.data.get('action')
        if action == 'approve':
            profile.is_approved = True
            profile.save()
            return Response({'message': f'{profile.business_name} approved.'})
        elif action == 'reject':
            profile.is_approved = False
            profile.save()
            return Response({'message': f'{profile.business_name} rejected.'})
        return Response({'error': 'Invalid action. Use approve or reject.'}, status=400)


class SellerListView(generics.ListAPIView):
    """Admin: list all sellers."""
    serializer_class = SellerProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get_queryset(self):
        is_approved = self.request.query_params.get('approved')
        qs = SellerProfile.objects.select_related('user')
        if is_approved is not None:
            qs = qs.filter(is_approved=is_approved.lower() == 'true')
        return qs
