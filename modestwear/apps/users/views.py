from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from apps.users.serializers import UserSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Handles GET /profile and PATCH /profile
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
