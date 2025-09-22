from django.contrib import admin
from .models import Movie

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'tmdb_id', 'release_date', 'vote_average', 'popularity']
    list_filter = ['release_date', 'vote_average']
    search_fields = ['title', 'tmdb_id']
    readonly_fields = ['created_at', 'updated_at']
