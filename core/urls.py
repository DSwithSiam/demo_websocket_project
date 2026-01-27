"""
Core App URL Configuration

This module defines URL patterns for the core app views and API endpoints.
It routes HTTP requests to the appropriate view handlers.

Documentation:
- Django URL Dispatcher: https://docs.djangoproject.com/en/6.0/topics/http/urls/

Author: WebSocket Demo Project
"""

from django.urls import path
from . import views

# ============================================================================
# URL PATTERNS
# ============================================================================
# Each pattern maps a URL route to a view function or class.
# The pattern syntax uses regular expressions for flexible routing.
# ============================================================================

app_name = 'core'  # Namespace for URL reversal

urlpatterns = [
    # Index/Home page - shows overview of all demos
    path('', views.websocket_demo_index, name='index'),
    
    # Chat room list page - shows available rooms
    path('chat/', views.chat_room_list, name='chat_list'),
    
    # Specific chat room - enter room name after /chat/room/
    # Example: /chat/room/general/
    path('chat/room/<str:room_name>/', views.chat_room, name='chat_room'),
    
    # Notifications page - real-time notifications demo
    path('notifications/', views.notifications_page, name='notifications'),
    
    # Counter page - synchronized counter demo
    path('counter/', views.counter_page, name='counter'),
    
    # API endpoint for sending notifications
    path('api/notifications/send/', views.SendNotificationView.as_view(), name='send_notification'),
]
