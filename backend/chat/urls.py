from django.urls import path
from .views import chat_view, schedule_meeting, update_availability,group_detail

urlpatterns = [
    path('messages/', chat_view, name='chat-messages'),
    path('schedule/', schedule_meeting, name='schedule-meeting'),
    path('availability/', update_availability, name='update-availability'),
     path('group/', group_detail, name='group-detail'),
]