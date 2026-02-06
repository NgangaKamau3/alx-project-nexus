from django.db.models import Count, Avg, Q
from django.contrib.auth import get_user_model
from apps.catalog.models import Product, Category
from apps.orders.models import OrderItem
from apps.outfits.models import OutfitItem
from collections import defaultdict
import math
from decimal import Decimal

User = get_user_model()

class RecommendationService:
    
    @staticmethod
    def get_recommendations(user=None, product=None, limit=10):
        """
        Main recommendation engine combining multiple strategies
        """
        recommendations = []
        
        if user:
            # User-based recommendations
            recommendations.extend(RecommendationService._collaborative_filtering(user, limit//3))
            recommendations.extend(RecommendationService._user_preference_based(user, limit//3))
        
        if product:
            # Product-based recommendations
            recommendations.extend(RecommendationService._content_based_filtering(product, limit//2))
        
        # Add popular items to fill remaining slots
        popular_items = RecommendationService._popularity_based(limit)
        recommendations.extend(popular_items)
        
        # Remove duplicates and limit results
        seen = set()
        unique_recommendations = []
        for item in recommendations:
            if item.id not in seen:
                seen.add(item.id)
                unique_recommendations.append(item)
                if len(unique_recommendations) >= limit:
                    break
        
        return unique_recommendations[:limit]
    
    @staticmethod
    def _collaborative_filtering(user, limit=5):
        """
        Find users with similar purchase patterns and recommend their items
        """
        # Get user's purchased products (through variants)
        user_products = set(
            Product.objects.filter(
                variants__orderitem__order__user=user
            ).values_list('id', flat=True)
        )
        
        if not user_products:
            return []
        
        # Find similar users (users who bought similar products)
        similar_users = (
            OrderItem.objects.filter(variant__product_id__in=user_products)
            .exclude(order__user=user)
            .values('order__user')
            .annotate(common_products=Count('variant__product_id', distinct=True))
            .order_by('-common_products')[:10]
        )
        
        similar_user_ids = [u['order__user'] for u in similar_users]
        
        # Get products bought by similar users that current user hasn't bought
        recommendations = (
            Product.objects.filter(
                variants__orderitem__order__user_id__in=similar_user_ids
            )
            .exclude(id__in=user_products)
            .annotate(recommendation_score=Count('variants__orderitem'))
            .order_by('-recommendation_score')[:limit]
        )
        
        return list(recommendations)
    
    @staticmethod
    def _content_based_filtering(product, limit=5):
        """
        Recommend similar products based on category, price range, etc.
        """
        price_range = product.base_price * Decimal('0.3')  # 30% price tolerance
        
        similar_products = (
            Product.objects.filter(
                category=product.category,
                base_price__gte=product.base_price - price_range,
                base_price__lte=product.base_price + price_range
            )
            .exclude(id=product.id)
            .order_by('-is_featured', '-date_added')[:limit]
        )
        
        return list(similar_products)
    
    @staticmethod
    def _user_preference_based(user, limit=5):
        """
        Recommend based on user's category preferences and outfit history
        """
        # Get user's favorite categories from purchase history
        favorite_categories = (
            Category.objects.filter(
                products__variants__orderitem__order__user=user
            )
            .annotate(purchase_count=Count('products__variants__orderitem'))
            .order_by('-purchase_count')[:3]
        )
        
        # Get user's outfit preferences
        outfit_categories = (
            Category.objects.filter(
                products__outfititem__outfit__user=user
            )
            .annotate(outfit_count=Count('products__outfititem'))
            .order_by('-outfit_count')[:3]
        )
        
        # Combine categories
        preferred_categories = list(favorite_categories) + list(outfit_categories)
        category_ids = [cat.id for cat in preferred_categories]
        
        if not category_ids:
            return []
        
        # Get user's purchased products to exclude
        purchased_products = set(
            Product.objects.filter(
                variants__orderitem__order__user=user
            ).values_list('id', flat=True)
        )
        
        recommendations = (
            Product.objects.filter(category_id__in=category_ids)
            .exclude(id__in=purchased_products)
            .order_by('-is_featured', '-date_added')[:limit]
        )
        
        return list(recommendations)
    
    @staticmethod
    def _popularity_based(limit=10):
        """
        Recommend popular products based on sales and outfit usage
        """
        popular_products = (
            Product.objects.annotate(
                sales_count=Count('variants__orderitem'),
                outfit_count=Count('outfititem'),
                popularity_score=Count('variants__orderitem') + Count('outfititem')
            )
            .filter(popularity_score__gt=0)
            .order_by('-popularity_score', '-is_featured', '-date_added')[:limit]
        )
        
        return list(popular_products)
    
    @staticmethod
    def get_trending_products(limit=10):
        """
        Get trending products based on recent activity
        """
        from datetime import datetime, timedelta
        
        last_week = datetime.now() - timedelta(days=7)
        
        trending = (
            Product.objects.filter(
                Q(variants__orderitem__order__created_at__gte=last_week) |
                Q(outfititem__outfit__created_at__gte=last_week)
            )
            .annotate(
                recent_activity=Count('variants__orderitem') + Count('outfititem')
            )
            .order_by('-recent_activity', '-date_added')[:limit]
        )
        
        return list(trending)
    
    @staticmethod
    def get_price_based_recommendations(product, limit=5):
        """
        Get products in similar price range
        """
        if product.base_price <= 50:
            price_min, price_max = Decimal('0'), Decimal('75')
        elif product.base_price <= 100:
            price_min, price_max = Decimal('25'), Decimal('150')
        else:
            price_min = product.base_price * Decimal('0.7')
            price_max = product.base_price * Decimal('1.5')
        
        similar_priced = (
            Product.objects.filter(
                base_price__gte=price_min,
                base_price__lte=price_max
            )
            .exclude(id=product.id)
            .order_by('-is_featured', '?')[:limit]  # Random order for variety
        )
        
        return list(similar_priced)