from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Movie
from .serializers import MovieSerializer, MovieListSerializer
from .services import tmdb_service
from .utils import sync_movie_to_db
from .recommendations import RecommendationEngine

@api_view(['GET'])
@permission_classes([AllowAny])
def trending_movies(request):
    time_window = request.GET.get('time_window', 'day')
    page = int(request.GET.get('page', 1))
    
    data = tmdb_service.get_trending_movies(time_window, page)
    if not data:
        return Response({'error': 'Failed to fetch trending movies'}, 
                       status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    # Sync movies to local database
    for movie_data in data.get('results', []):
        sync_movie_to_db(movie_data)
    
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommendations(request):
    user_recommendations = RecommendationEngine.get_recommendations_for_user(request.user)
    serializer = MovieListSerializer(user_recommendations, many=True)
    return Response(serializer.data)
