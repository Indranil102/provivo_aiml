from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Message, Meeting, Availability, Group
from .serializers import MessageSerializer, MeetingSerializer, AvailabilitySerializer
from .nlp import MeetingIntentDetector
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import uuid
from rest_framework.permissions import AllowAny   # ← import

from .serializers import GroupSerializer

@api_view(['GET'])
@permission_classes([AllowAny])          # open to anyone
def group_list(request):
    groups = Group.objects.all()
    return Response(GroupSerializer(groups, many=True).data)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def group_detail(request):
    group = request.user.group
    if not group:
        return Response({'error': 'User not in any group'}, 400)
    return Response(GroupSerializer(group).data)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def chat_view(request):
    user = request.user
    group = user.group
    
    if not group:
        return Response({'error': 'User not assigned to any group'}, status=400)
    
    if request.method == 'GET':
        messages = Message.objects.filter(group=group)[:50]
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        content = request.data.get('content', '')
        
        # Save message
        message = Message.objects.create(
            user=user,
            group=group,
            content=content
        )
        
        # Check for meeting intent
        nlp_result = MeetingIntentDetector.process_message(content)
        
        response_data = {
            'message': MessageSerializer(message).data,
            'nlp_analysis': nlp_result
        }
        
        # If meeting intent detected, create a pending meeting
        if nlp_result['has_meeting_intent']:
            meeting = Meeting.objects.create(
                group=group,
                title=f"Meeting initiated by {user.username}",
                description=content,
                scheduled_time=timezone.now() + timezone.timedelta(hours=1),
                google_meet_link=f"https://meet.google.com/{uuid.uuid4().hex[:10]}",
                creator=user
            )
            
            # Create availability entries for all group members
            for member in group.user_set.all():
                Availability.objects.create(
                    user=member,
                    meeting=meeting
                )
            
            response_data['meeting'] = MeetingSerializer(meeting).data
        
        return Response(response_data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def schedule_meeting(request):
    meeting_id = request.data.get('meeting_id')
    time = request.data.get('time')
    
    try:
        meeting = Meeting.objects.get(id=meeting_id, group=request.user.group)
        meeting.scheduled_time = time
        meeting.save()
        
        # Here you would integrate with Google Calendar API
        # For now, just return success
        
        return Response({'status': 'meeting scheduled'})
    except Meeting.DoesNotExist:
        return Response({'error': 'Meeting not found'}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_availability(request):
    meeting_id = request.data.get('meeting_id')
    is_available = request.data.get('is_available')
    
    try:
        availability = Availability.objects.get(
            meeting_id=meeting_id,
            user=request.user
        )
        availability.is_available = is_available
        availability.save()
        
        return Response({'status': 'availability updated'})
    except Availability.DoesNotExist:
        return Response({'error': 'Availability not found'}, status=404)