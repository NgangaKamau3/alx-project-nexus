from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserCreateSerializer(serializers.ModelSerializer):
    profile_picure_url = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'profile_picture', 'profile_picture_url', 'phone_number', 'created_at')
        read_only_fields = ['id', 'email', 'created_at', 'is_verified', 'profile_picture_url']
        
    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            return self.context['request'].build_absolute_uri(obj.profile_picture_url)
        return None