from rest_framework import serializers
from .models import Category, Product, ProductImage, Review


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'parent', 'children', 'is_active']

    def get_children(self, obj):
        children = obj.children.filter(is_active=True)
        return CategorySerializer(children, many=True).data


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_primary', 'alt_text', 'order']


class ReviewSerializer(serializers.ModelSerializer):
    buyer_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'buyer_name', 'rating', 'title', 'comment', 'is_verified_purchase', 'created_at']
        read_only_fields = ['is_verified_purchase', 'created_at']

    def get_buyer_name(self, obj):
        return obj.buyer.full_name

    def create(self, validated_data):
        validated_data['buyer'] = self.context['request'].user
        return super().create(validated_data)


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing."""
    primary_image = serializers.SerializerMethodField()
    avg_rating = serializers.ReadOnlyField()
    discount_percent = serializers.ReadOnlyField()
    effective_price = serializers.ReadOnlyField()
    seller_name = serializers.CharField(source='seller.business_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'seller_name', 'category_name',
            'price', 'discount_price', 'effective_price', 'discount_percent',
            'stock', 'status', 'is_featured', 'avg_rating', 'review_count',
            'primary_image', 'created_at',
        ]

    def get_primary_image(self, obj):
        img = obj.primary_image
        if img:
            request = self.context.get('request')
            return request.build_absolute_uri(img.image.url) if request else img.image.url
        return None

    def get_review_count(self, obj):
        return obj.reviews.count()


class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    avg_rating = serializers.ReadOnlyField()
    discount_percent = serializers.ReadOnlyField()
    effective_price = serializers.ReadOnlyField()
    seller = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'seller', 'category', 'description',
            'price', 'discount_price', 'effective_price', 'discount_percent',
            'stock', 'status', 'sku', 'weight', 'is_featured',
            'avg_rating', 'views_count', 'images', 'reviews', 'created_at',
        ]

    def get_seller(self, obj):
        return {
            'id': obj.seller.id,
            'business_name': obj.seller.business_name,
            'business_description': obj.seller.business_description,
        }


class ProductWriteSerializer(serializers.ModelSerializer):
    """For seller product creation/update."""
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'description', 'price', 'discount_price',
            'stock', 'status', 'sku', 'weight', 'is_featured',
        ]

    def create(self, validated_data):
        validated_data['seller'] = self.context['request'].user.seller_profile
        return super().create(validated_data)
