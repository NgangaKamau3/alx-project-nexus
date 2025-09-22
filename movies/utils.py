from datetime import datetime
from .models import Movie
from .services import tmdb_service

def sync_movie_to_db(movie_data):
    """Sync movie data from TMDb API to local database"""
    try:
        release_date = None
        if movie_data.get('release_date'):
            release_date = datetime.strptime(movie_data['release_date'], '%Y-%m-%d').date()
        
        movie, created = Movie.objects.update_or_create(
            tmdb_id=movie_data['id'],
            defaults={
                'title': movie_data.get('title', ''),
                'overview': movie_data.get('overview', ''),
                'release_date': release_date,
                'poster_path': movie_data.get('poster_path', ''),
                'backdrop_path': movie_data.get('backdrop_path', ''),
                'vote_average': movie_data.get('vote_average', 0.0),
                'vote_count': movie_data.get('vote_count', 0),
                'popularity': movie_data.get('popularity', 0.0),
                'genre_ids': movie_data.get('genre_ids', []),
            }
        )
        return movie
    except Exception as e:
        print(f"Error syncing movie {movie_data.get('id')}: {e}")
        return None