from django.db.models import Q, Count
from django.core.cache import cache
from .models import Movie
from users.models import FavoriteMovie

class RecommendationEngine:
    @staticmethod
    def get_recommendations_for_user(user, limit=20):
        cache_key = f"recommendations_{user.id}"
        cached_recommendations = cache.get(cache_key)
        
        if cached_recommendations:
            return cached_recommendations
        
        # Get user's favorite genres from their favorite movies
        favorite_movies = FavoriteMovie.objects.filter(user=user).select_related('movie')
        
        if not favorite_movies.exists():
            # Return popular movies for new users
            recommendations = Movie.objects.order_by('-popularity')[:limit]
        else:
            # Get genres from favorite movies
            favorite_genres = set()
            for fav in favorite_movies:
                favorite_genres.update(fav.movie.genre_ids)
            
            # Get movies with similar genres, excluding already favorited
            favorited_ids = [fav.movie.tmdb_id for fav in favorite_movies]
            
            recommendations = Movie.objects.filter(
                genre_ids__overlap=list(favorite_genres)
            ).exclude(
                tmdb_id__in=favorited_ids
            ).order_by('-vote_average', '-popularity')[:limit]
        
        recommendations_list = list(recommendations)
        cache.set(cache_key, recommendations_list, timeout=1800)  # 30 minutes
        
        return recommendations_list
    
    @staticmethod
    def invalidate_user_recommendations(user):
        cache_key = f"recommendations_{user.id}"
        cache.delete(cache_key)