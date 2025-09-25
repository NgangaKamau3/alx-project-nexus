from django.contrib.auth.models import User
from django.db import transaction
from .models import UserProfile, FavoriteMovie
from movies.models import Movie

class UserService:
    @staticmethod
    def create_user_with_profile(username, email, password, preferred_genres=None):
        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            if preferred_genres:
                user.profile.preferred_genres = preferred_genres
                user.profile.save()
            return user
    
    @staticmethod
    def add_favorite_movie(user, tmdb_id):
        try:
            movie = Movie.objects.get(tmdb_id=tmdb_id)
            favorite, created = FavoriteMovie.objects.get_or_create(
                user=user,
                movie=movie
            )
            return favorite, created
        except Movie.DoesNotExist:
            return None, False
    
    @staticmethod
    def remove_favorite_movie(user, tmdb_id):
        try:
            movie = Movie.objects.get(tmdb_id=tmdb_id)
            deleted_count, _ = FavoriteMovie.objects.filter(
                user=user,
                movie=movie
            ).delete()
            return deleted_count > 0
        except Movie.DoesNotExist:
            return False