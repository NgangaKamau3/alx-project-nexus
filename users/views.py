from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import FavoriteMovie
from .serializers import UserRegistrationSerializer, UserProfileSerializer, FavoriteMovieSerializer
from .services import UserService
from movies.recommendations import RecommendationEngine

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    if request.method == 'GET':
        serializer = UserProfileSerializer(request.user.profile)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = UserProfileSerializer(request.user.profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            RecommendationEngine.invalidate_user_recommendations(request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def favorite_movie(request, tmdb_id):
    if request.method == 'POST':
        favorite, created = UserService.add_favorite_movie(request.user, tmdb_id)
        if favorite:
            RecommendationEngine.invalidate_user_recommendations(request.user)
            return Response({'message': 'Movie added to favorites'}, 
                          status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        return Response({'error': 'Movie not found'}, status=status.HTTP_404_NOT_FOUND)
    
    elif request.method == 'DELETE':
        removed = UserService.remove_favorite_movie(request.user, tmdb_id)
        if removed:
            RecommendationEngine.invalidate_user_recommendations(request.user)
            return Response({'message': 'Movie removed from favorites'})
        return Response({'error': 'Movie not in favorites'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_favorites(request):
    favorites = FavoriteMovie.objects.filter(user=request.user).select_related('movie')
    serializer = FavoriteMovieSerializer(favorites, many=True)
    return Response(serializer.data)
