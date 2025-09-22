import requests
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class TMDbService:
    def __init__(self):
        self.api_key = settings.TMDB_API_KEY
        self.base_url = settings.TMDB_BASE_URL
        self.session = requests.Session()
        self.session.params = {'api_key': self.api_key}
    
    def _make_request(self, endpoint, params=None):
        try:
            url = f"{self.base_url}/{endpoint}"
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"TMDb API request failed: {e}")
            return None

    def get_trending_movies(self, time_window='day', page=1):
        cache_key = f"trending_movies_{time_window}_{page}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        endpoint = f"trending/movie/{time_window}"
        params = {'page': page}
        data = self._make_request(endpoint, params)
        
        if data:
            cache.set(cache_key, data, timeout=3600)  # Cache for 1 hour
        
        return data

tmdb_service = TMDbService()