"""
WebSocket Views Module

This module contains Django views for rendering WebSocket demo pages.
Each view serves an HTML page that demonstrates a specific WebSocket use case.

Documentation:
- Django Views: https://docs.djangoproject.com/en/6.0/topics/http/views/
- Django Templates: https://docs.djangoproject.com/en/6.0/topics/templates/

Author: WebSocket Demo Project
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
import json


# ============================================================================
# CHAT ROOM VIEW
# ============================================================================
# View for displaying the chat room interface
# ============================================================================

def chat_room_list(request):
    """
    View to display list of available chat rooms.
    
    This view shows all available chat rooms and allows users to join them.
    
    Args:
        request: Django HTTP request object
        
    Returns:
        Rendered HTML template with list of chat rooms
    """
    # List of demo chat rooms
    rooms = [
        {'name': 'general', 'description': 'General discussion room'},
        {'name': 'tech', 'description': 'Technology discussions'},
        {'name': 'random', 'description': 'Random chit-chat'},
    ]
    
    context = {
        'rooms': rooms,
        'page_title': 'Chat Rooms',
    }
    
    return render(request, 'core/chat_room_list.html', context)


def chat_room(request, room_name):
    """
    View to display a specific chat room.
    
    This view renders the chat interface for a specific room.
    Users will connect to this room via WebSocket from this page.
    
    Args:
        request: Django HTTP request object
        room_name (str): Name of the chat room
        
    Returns:
        Rendered HTML template for the chat room
    """
    context = {
        'room_name': room_name,
        'page_title': f'Chat Room - {room_name}',
        'ws_scheme': 'wss' if request.is_secure() else 'ws',
        'host': request.get_host(),
    }
    
    return render(request, 'core/chat_room.html', context)


# ============================================================================
# NOTIFICATION VIEW
# ============================================================================
# View for displaying real-time notifications
# ============================================================================

def notifications_page(request):
    """
    View to display notifications interface.
    
    This page demonstrates real-time notifications from server to client.
    Users connect via WebSocket to receive updates.
    
    Args:
        request: Django HTTP request object
        
    Returns:
        Rendered HTML template for notifications
    """
    context = {
        'page_title': 'Real-time Notifications',
        'ws_scheme': 'wss' if request.is_secure() else 'ws',
        'host': request.get_host(),
        'user_id': request.user.id if request.user.is_authenticated else 'guest',
    }
    
    return render(request, 'core/notifications.html', context)


# ============================================================================
# COUNTER VIEW
# ============================================================================
# View for displaying real-time counter
# ============================================================================

def counter_page(request):
    """
    View to display real-time counter interface.
    
    This page demonstrates synchronized real-time counter across all users.
    
    Args:
        request: Django HTTP request object
        
    Returns:
        Rendered HTML template for counter
    """
    context = {
        'page_title': 'Real-time Counter',
        'ws_scheme': 'wss' if request.is_secure() else 'ws',
        'host': request.get_host(),
    }
    
    return render(request, 'core/counter.html', context)


# ============================================================================
# API ENDPOINT VIEWS
# ============================================================================
# Views for REST API endpoints used by WebSocket demos
# ============================================================================

class SendNotificationView(View):
    """
    View to manually send notifications to users.
    
    This is a demo endpoint that allows sending notifications via HTTP,
    which are then broadcasted to connected WebSocket clients.
    
    Usage:
        POST /api/notifications/send/
        {
            "title": "New Message",
            "message": "You have a new message",
            "priority": "high"
        }
    """
    
    @method_decorator(require_http_methods(["POST"]))
    def post(self, request):
        """
        Handle POST request to send notification.
        
        Args:
            request: Django HTTP request with JSON body
            
        Returns:
            JsonResponse with status and message
        """
        try:
            # Parse JSON request body
            data = json.loads(request.body)
            
            # Validate required fields
            title = data.get('title', '')
            message = data.get('message', '')
            priority = data.get('priority', 'normal')
            
            if not title or not message:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Title and message are required'
                }, status=400)
            
            # In a real application, you would broadcast this via channels
            # For now, we just return success
            return JsonResponse({
                'status': 'success',
                'message': 'Notification sent',
                'data': {
                    'title': title,
                    'message': message,
                    'priority': priority
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON format'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)


@require_http_methods(["GET"])
def websocket_demo_index(request):
    """
    Main WebSocket demo index page.
    
    Shows overview of all WebSocket demos available.
    
    Args:
        request: Django HTTP request object
        
    Returns:
        Rendered HTML template with demo index
    """
    demos = [
        {
            'name': 'Chat Room',
            'url': '/chat/',
            'description': 'Real-time multi-user chat',
            'features': ['Message broadcasting', 'User join/leave notifications', 'Room-based grouping']
        },
        {
            'name': 'Notifications',
            'url': '/notifications/',
            'description': 'Real-time notifications',
            'features': ['Server-to-client messaging', 'User-specific notifications', 'Priority levels']
        },
        {
            'name': 'Counter',
            'url': '/counter/',
            'description': 'Synchronized real-time counter',
            'features': ['Synchronized state', 'Increment/Decrement', 'Global counter']
        },
    ]
    
    context = {
        'page_title': 'WebSocket Demos',
        'demos': demos,
    }
    
    return render(request, 'core/index.html', context)
