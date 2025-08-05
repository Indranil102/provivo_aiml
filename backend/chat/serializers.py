from rest_framework import serializers
from .models import Message, Meeting, Availability, Group
from users.serializers import UserSerializer


class GroupSerializer(serializers.ModelSerializer):
    members = UserSerializer(source='group_members', many=True, read_only=True)

    class Meta:
        model = Group
        fields = ('id', 'name', 'members')


class MessageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = '__all__'


class MeetingSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    suggested_times = serializers.ListField(required=False, read_only=True)  # ✅ added dynamic field

    class Meta:
        model = Meeting
        fields = '__all__'  # includes all model fields + suggested_times
        read_only_fields = ['google_meet_link']


class AvailabilitySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Availability
        fields = '__all__'
