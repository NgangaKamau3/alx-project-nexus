from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.catalog.models import Category, Product
from apps.orders.models import Order, OrderItem
from apps.outfits.models import Outfit, OutfitItem
import random
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate sample data for testing recommendations'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating sample data for recommendations...')
        
        # Create categories
        categories_data = [
            ('Dresses', 'dresses'),
            ('Tops', 'tops'),
            ('Bottoms', 'bottoms'),
            ('Outerwear', 'outerwear'),
            ('Accessories', 'accessories'),
        ]
        
        categories = {}
        for name, slug in categories_data:
            category, created = Category.objects.get_or_create(
                slug=slug,
                defaults={'name': name}
            )
            categories[slug] = category
            if created:
                self.stdout.write(f'Created category: {name}')
        
        # Create products
        products_data = [
            ('Modest Maxi Dress', 'modest-maxi-dress', 'dresses', 89.99),
            ('Elegant Midi Dress', 'elegant-midi-dress', 'dresses', 79.99),
            ('Casual Day Dress', 'casual-day-dress', 'dresses', 59.99),
            ('Long Sleeve Blouse', 'long-sleeve-blouse', 'tops', 45.99),
            ('Modest Tunic Top', 'modest-tunic-top', 'tops', 39.99),
            ('High-Neck Sweater', 'high-neck-sweater', 'tops', 55.99),
            ('Wide Leg Pants', 'wide-leg-pants', 'bottoms', 65.99),
            ('Modest Skirt', 'modest-skirt', 'bottoms', 49.99),
            ('Long Cardigan', 'long-cardigan', 'outerwear', 75.99),
            ('Modest Blazer', 'modest-blazer', 'outerwear', 95.99),
        ]
        
        products = {}
        for name, slug, category_slug, price in products_data:
            product, created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'category': categories[category_slug],
                    'base_price': Decimal(str(price)),
                    'description': f'Beautiful {name.lower()} for modest fashion',
                    'is_featured': random.choice([True, False])
                }
            )
            products[slug] = product
            if created:
                self.stdout.write(f'Created product: {name}')
        
        # Create test users
        test_users = []
        for i in range(5):
            username = f'testuser{i+1}'
            try:
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': f'{username}@example.com',
                        'password': 'pbkdf2_sha256$600000$temp$invalid'
                    }
                )
                test_users.append(user)
                if created:
                    self.stdout.write(f'Created user: {username}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating user {username}: {str(e)}'))
                continue
        
        # Create sample orders for collaborative filtering
        product_list = list(products.values())
        for user in test_users:
            # Create 2-3 orders per user
            for _ in range(random.randint(2, 3)):
                order = Order.objects.create(
                    user=user,
                    total_amount=Decimal('0.00'),
                    status='completed'
                )
                
                # Add 1-3 items per order
                order_total = Decimal('0.00')
                for _ in range(random.randint(1, 3)):
                    product = random.choice(product_list)
                    quantity = random.randint(1, 2)
                    
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=product.base_price
                    )
                    order_total += product.base_price * quantity
                
                order.total_amount = order_total
                order.save()
        
        # Create sample outfits
        for user in test_users:
            for i in range(random.randint(1, 3)):
                outfit = Outfit.objects.create(
                    user=user,
                    name=f'{user.username} Outfit {i+1}',
                    description='A beautiful modest outfit',
                    is_public=random.choice([True, False])
                )
                
                # Add 2-4 products to each outfit
                selected_products = random.sample(product_list, random.randint(2, 4))
                for pos, product in enumerate(selected_products):
                    OutfitItem.objects.create(
                        outfit=outfit,
                        product=product,
                        position=pos
                    )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data for recommendations!')
        )