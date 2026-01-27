"""
WebSocket URL Routing Configuration

This module defines all WebSocket consumer routes for the application.
WebSocket consumers handle real-time bidirectional communication between 
clients and the server.

Documentation:
- Django Channels: https://channels.readthedocs.io/
- WebSocket Protocol: https://tools.ietf.org/html/rfc6455

Usage:
    from django.urls import re_path
    from core import consumers

    websocket_urlpatterns = [
        re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
    ]
"""

from django.urls import re_path
from core import consumers

# ============================================================================
# WebSocket URL Patterns
# ============================================================================
# Each pattern maps a WebSocket URL to its corresponding consumer class
# The 'as_asgi()' method converts the consumer to an ASGI application
# 
# Example URL patterns:
# - ws://localhost:8000/ws/chat/room1/ -> ChatConsumer
# - ws://localhost:8000/ws/notifications/ -> NotificationConsumer
# ============================================================================

websocket_urlpatterns = [
    # Chat WebSocket endpoint
    # Usage: connect to ws://localhost:8000/ws/chat/{room_name}/
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
    
    # Notification WebSocket endpoint
    # Usage: connect to ws://localhost:8000/ws/notifications/
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
    
    # Real-time counter WebSocket endpoint
    # Usage: connect to ws://localhost:8000/ws/counter/
    re_path(r'ws/counter/$', consumers.CounterConsumer.as_asgi()),
]
