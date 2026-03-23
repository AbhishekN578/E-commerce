from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .models import Category, Product, ProductImage, Review
from .serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer,
    ProductWriteSerializer, ProductImageSerializer, ReviewSerializer
)
from .filters import ProductFilter
from accounts.permissions import IsSeller


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.filter(is_active=True, parent=None)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class ProductListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['price', 'created_at', 'views_count']
    ordering = ['-created_at']

    def get_queryset(self):
        return Product.objects.filter(status='active').select_related('seller', 'category').prefetch_related('images', 'reviews')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductWriteSerializer
        return ProductListSerializer

    def perform_create(self, serializer):
        if not self.request.user.role == 'seller' or not self.request.user.seller_profile.is_approved:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Only approved sellers can add products.')
        serializer.save(seller=self.request.user.seller_profile)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related('seller', 'category').prefetch_related('images', 'reviews__buyer')
    lookup_field = 'slug'
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProductWriteSerializer
        return ProductDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Track views
        Product.objects.filter(pk=instance.pk).update(views_count=instance.views_count + 1)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            if request.user.role != 'admin' and obj.seller.user != request.user:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied('You can only modify your own products.')


class ProductImageUploadView(generics.CreateAPIView):
    serializer_class = ProductImageSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def perform_create(self, serializer):
        product = get_object_or_404(Product, slug=self.kwargs['slug'], seller=self.request.user.seller_profile)
        # If first image, set as primary
        is_primary = not product.images.exists()
        serializer.save(product=product, is_primary=is_primary)


class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        product = get_object_or_404(Product, slug=self.kwargs['slug'])
        # Verify purchase
        from orders.models import OrderItem
        is_verified = OrderItem.objects.filter(
            order__buyer=self.request.user,
            product=product,
            status='delivered'
        ).exists()
        serializer.save(product=product, buyer=self.request.user, is_verified_purchase=is_verified)


class ReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Review.objects.filter(product__slug=self.kwargs['slug']).select_related('buyer')


class SellerProductListView(generics.ListAPIView):
    """Seller's own products (all statuses)."""
    serializer_class = ProductListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(
            seller=self.request.user.seller_profile
        ).select_related('category').prefetch_related('images')
