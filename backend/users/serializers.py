# user/serializers.py
from rest_framework import serializers
from chat.models import Group
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'group')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        from .models import UserProfile
        UserProfile.objects.create(user=user)
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()