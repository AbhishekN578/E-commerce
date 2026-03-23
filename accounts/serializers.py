from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, SellerProfile, BuyerProfile


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=['buyer', 'seller'], default='buyer')

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'role', 'password', 'password2']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(**validated_data)
        if user.role == 'buyer':
            BuyerProfile.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid credentials.')
        if not user.is_active:
            raise serializers.ValidationError('Account is disabled.')
        refresh = RefreshToken.for_user(user)
        return {
            'user': user,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'role', 'avatar', 'date_joined']
        read_only_fields = ['id', 'role', 'date_joined']


class SellerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    total_products = serializers.SerializerMethodField()

    class Meta:
        model = SellerProfile
        fields = [
            'id', 'user', 'business_name', 'business_description', 'business_logo',
            'is_approved', 'stripe_onboarding_complete', 'phone', 'address',
            'total_sales', 'total_products', 'created_at'
        ]
        read_only_fields = ['is_approved', 'stripe_onboarding_complete', 'total_sales']

    def get_total_products(self, obj):
        return obj.products.filter(status='active').count()


class CreateSellerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerProfile
        fields = ['business_name', 'business_description', 'business_logo', 'phone', 'address']

    def create(self, validated_data):
        user = self.context['request'].user
        return SellerProfile.objects.create(user=user, **validated_data)


class BuyerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = BuyerProfile
        fields = ['id', 'user', 'phone', 'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country']
