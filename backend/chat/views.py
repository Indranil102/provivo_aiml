from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Message, Meeting, Availability, Group
from .serializers import MessageSerializer, MeetingSerializer, AvailabilitySerializer, GroupSerializer
from .nlp import MeetingIntentDetector
from google.oauth2 import service_account
from googleapiclient.discovery import build
import uuid
import os
import datetime

# Load Google credentials
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), 'service_account.json')
SCOPES = ['https://www.googleapis.com/auth/calendar']

def create_google_meet_link(summary, description, start_datetime, end_datetime):
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )

        service = build("calendar", "v3", credentials=credentials)
        calendar_id = 'primary'  # Or use a shared calendar's email

        event = {
            "summary": summary,
            "description": description,
            "start": {
                "dateTime": start_datetime.isoformat(),
                "timeZone": "UTC",
            },
            "end": {
                "dateTime": end_datetime.isoformat(),
                "timeZone": "UTC",
            },
            "conferenceData": {
                "createRequest": {
                    "conferenceSolutionKey": {
                        "type": "hangoutsMeet"
                    },
                    "requestId": f"meet-{uuid.uuid4().hex[:8]}"
                }
            }
        }

        created_event = service.events().insert(
            calendarId=calendar_id,
            body=event,
            conferenceDataVersion=1
        ).execute()

        meet_link = created_event["hangoutLink"]
        return meet_link

    except Exception as e:
        print("❌ Google Meet API Error:", str(e))
        return None


@api_view(['GET'])
@permission_classes([AllowAny])
def group_list(request):
    groups = Group.objects.all()
    return Response(GroupSerializer(groups, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def group_detail(request):
    group = request.user.group
    if not group:
        return Response({'error': 'User not in any group'}, status=400)
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
        message = Message.objects.create(user=user, group=group, content=content)

        # NLP analysis
        nlp_result = MeetingIntentDetector.process_message(content)
        print("[DEBUG] NLP Result:", nlp_result)

        response_data = {
            'message': MessageSerializer(message).data,
            'nlp_analysis': nlp_result
        }

        if nlp_result['has_meeting_intent']:
            suggested_times = nlp_result.get("suggested_times", [])
            fallback_time = timezone.now() + timezone.timedelta(hours=1)

            # Prefer suggested time if available
            start_dt = timezone.datetime.fromisoformat(suggested_times[0]) if suggested_times else fallback_time
            end_dt = start_dt + timezone.timedelta(hours=1)

            # Create real Google Meet link
            meet_link = create_google_meet_link(
                summary=f"Meeting initiated by {user.username}",
                description=content,
                start_datetime=start_dt,
                end_datetime=end_dt
            )

            meeting = Meeting.objects.create(
                group=group,
                title=f"Meeting initiated by {user.username}",
                description=content,
                scheduled_time=start_dt,
                google_meet_link="https://meet.google.com/xvp-mfko-qwz",
                creator=user
            )

            for member in group.user_set.all():
                Availability.objects.create(user=member, meeting=meeting)

            meeting.suggested_times = suggested_times
            serialized = MeetingSerializer(meeting).data
            serialized["suggested_times"] = suggested_times

            response_data["meeting"] = serialized

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

        return Response({'status': 'meeting scheduled'})
    except Meeting.DoesNotExist:
        return Response({'error': 'Meeting not found'}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_availability(request):
    meeting_id = request.data.get('meeting_id')
    is_available = request.data.get('is_available')

    try:
        availability = Availability.objects.get(meeting_id=meeting_id, user=request.user)
        availability.is_available = is_available
        availability.save()

        return Response({'status': 'availability updated'})
    except Availability.DoesNotExist:
        return Response({'error': 'Availability not found'}, status=404)
