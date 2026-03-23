import os
import random
import requests
from io import BytesIO
from django.core.management.base import BaseCommand
from django.core.files.images import ImageFile
from django.utils.text import slugify
from accounts.models import CustomUser, SellerProfile, BuyerProfile
from products.models import Category, Product, ProductImage

class Command(BaseCommand):
    help = 'Populates the database with dummy data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating data...')

        # Categories
        categories_data = ['Electronics', 'Fashion', 'Home', 'Books']
        categories = []
        for cat_name in categories_data:
            cat, created = Category.objects.get_or_create(name=cat_name, defaults={'slug': slugify(cat_name)})
            categories.append(cat)

        # Sellers
        seller_users = []
        for i in range(1, 4):
            email = f'seller{i}@ecommerce.com'
            user, created = CustomUser.objects.get_or_create(email=email, defaults={'role': 'seller', 'first_name': f'Seller{i}', 'last_name': 'Test'})
            if created:
                user.set_password('seller123')
                user.save()
                SellerProfile.objects.create(user=user, business_name=f'Awesome Store {i}', is_approved=True)
            seller_users.append(user)

        # Products
        products_data = [
            {'name': 'Wireless Noise Cancelling Headphones', 'cat': 'Electronics', 'price': 15000, 'is_featured': True},
            {'name': '4K Ultra HD Smart TV 55-inch', 'cat': 'Electronics', 'price': 45000, 'is_featured': True},
            {'name': 'Men\'s Classic Fit Suit', 'cat': 'Fashion', 'price': 8000, 'is_featured': False},
            {'name': 'Women\'s Running Shoes', 'cat': 'Fashion', 'price': 4500, 'is_featured': True},
            {'name': 'Stainless Steel Cookware Set', 'cat': 'Home', 'price': 6000, 'is_featured': False},
            {'name': 'Robot Vacuum Cleaner', 'cat': 'Home', 'price': 12000, 'is_featured': True},
            {'name': 'The Great Gatsby - Hardcover', 'cat': 'Books', 'price': 800, 'is_featured': False},
            {'name': 'Python Crash Course, 3rd Edition', 'cat': 'Books', 'price': 1200, 'is_featured': True},
            {'name': 'Smart Watch Series 8', 'cat': 'Electronics', 'price': 22000, 'is_featured': False},
            {'name': 'Designer Sunglasses', 'cat': 'Fashion', 'price': 3000, 'is_featured': False},
        ]

        # Use Picsum for random images
        # Different id for each to get a different image
        image_idx = 100
        for item_data in products_data:
            cat = Category.objects.get(name=item_data['cat'])
            seller_user = random.choice(seller_users)
            
            product, created = Product.objects.get_or_create(
                name=item_data['name'],
                defaults={
                    'slug': slugify(item_data['name']),
                    'seller': seller_user.seller_profile,
                    'category': cat,
                    'description': f"This is an amazing {item_data['name']}. It offers great value and premium quality.",
                    'price': item_data['price'] * 1.2,
                    'discount_price': item_data['price'],
                    'stock': random.randint(10, 100),
                    'status': 'active',
                    'is_featured': item_data['is_featured'],
                }
            )

            if created:
                # Add images
                try:
                    for i in range(2): # 2 images per product
                        image_idx += 1
                        url = f"https://picsum.photos/id/{image_idx}/600/600"
                        response = requests.get(url, timeout=10)
                        if response.status_code == 200:
                            img_io = BytesIO(response.content)
                            file = ImageFile(img_io, name=f"{product.slug}-{i}.jpg")
                            ProductImage.objects.create(
                                product=product,
                                image=file,
                                is_primary=(i==0)
                            )
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Failed to fetch image for {product.name}: {e}"))
                self.stdout.write(f"Created product: {product.name}")

        self.stdout.write(self.style.SUCCESS('Successfully populated dummy data.'))
