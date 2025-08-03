# backend/meeting_scheduler/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse  # ← add this import

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/chat/', include('chat.urls')),
    path('', lambda _: JsonResponse({'status': 'API is running on /api/'})),  # ← new line
]