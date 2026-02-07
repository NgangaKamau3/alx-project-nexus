from rest_framework import serializers
from apps.users.models import User
from dj_rest_auth.registration.serializers import RegisterSerializer


class UserSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'profile_picture', 'profile_picture_url', 'phone_number', 'created_at')
        read_only_fields = ['id', 'email', 'created_at', 'is_verified', 'profile_picture_url']
        
    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            return self.context['request'].build_absolute_uri(obj.profile_picture.url)
        return None

class CustomRegisterSerializer(RegisterSerializer):
    username = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    
    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['username'] = self.validated_data.get('username', '')
        data['first_name'] = self.validated_data.get('first_name', '')
        data['last_name'] = self.validated_data.get('last_name', '')
        return data