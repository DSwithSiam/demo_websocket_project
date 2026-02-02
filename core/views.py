"""
Core App API Views

This module contains REST API endpoints for WebSocket chat application.
Pure API views with Swagger documentation.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Chat, ChatMessage


# ============================================================================
# CHAT ROOM API ENDPOINTS
# ============================================================================

@swagger_auto_schema(
    method='get',
    operation_description="Get list of all chat rooms",
    responses={
        200: openapi.Response(
            description="List of chat rooms",
            examples={
                "application/json": {
                    "count": 2,
                    "rooms": [
                        {"room_name": "general", "message_count": 10},
                        {"room_name": "tech", "message_count": 5}
                    ]
                }
            }
        )
    },
    tags=['Chat Rooms']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def list_chat_rooms(request):
    """
    Get list of all available chat rooms with message counts.
    """
    try:
        # Get distinct room names from ChatMessage
        rooms = ChatMessage.objects.values('room_name').distinct()
        
        room_data = []
        for room in rooms:
            room_name = room['room_name']
            message_count = ChatMessage.objects.filter(room_name=room_name).count()
            last_message = ChatMessage.objects.filter(room_name=room_name).order_by('-timestamp').first()
            
            room_data.append({
                'room_name': room_name,
                'message_count': message_count,
                'last_message_time': last_message.timestamp.isoformat() if last_message else None
            })
        
        return Response({
            'count': len(room_data),
            'rooms': room_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='post',
    operation_description="Create a new chat room",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['room_name'],
        properties={
            'room_name': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description='Name of the chat room',
                example='general'
            ),
            'initial_message': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description='Optional initial message',
                example='Welcome to the room!'
            )
        }
    ),
    responses={
        201: openapi.Response(
            description="Room created successfully",
            examples={
                "application/json": {
                    "message": "Room created successfully",
                    "room": {"room_name": "general"}
                }
            }
        ),
        400: "Bad request - room_name is required"
    },
    tags=['Chat Rooms']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def create_chat_room(request):
    """
    Create a new chat room with an optional initial message.
    """
    try:
        room_name = request.data.get('room_name')
        initial_message = request.data.get('initial_message', 'Room created')
        
        if not room_name:
            return Response({
                'error': 'room_name is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create initial chat entry
        chat = Chat.objects.create(
            room_name=room_name,
            message=initial_message
        )
        
        return Response({
            'message': 'Room created successfully',
            'room': {
                'room_name': chat.room_name
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# CHAT HISTORY API ENDPOINTS
# ============================================================================

@swagger_auto_schema(
    method='get',
    operation_description="Get chat history for a specific room",
    manual_parameters=[
        openapi.Parameter(
            'room_name',
            openapi.IN_PATH,
            description="Name of the chat room",
            type=openapi.TYPE_STRING,
            required=True
        ),
        openapi.Parameter(
            'limit',
            openapi.IN_QUERY,
            description="Number of messages to return (default: 50)",
            type=openapi.TYPE_INTEGER,
            required=False
        ),
        openapi.Parameter(
            'offset',
            openapi.IN_QUERY,
            description="Offset for pagination (default: 0)",
            type=openapi.TYPE_INTEGER,
            required=False
        )
    ],
    responses={
        200: openapi.Response(
            description="Chat history retrieved successfully",
            examples={
                "application/json": {
                    "room_name": "general",
                    "messages": [
                        {
                            "id": 1,
                            "user_id": 1,
                            "user_email": "user@example.com",
                            "username": "john",
                            "message": "Hello!",
                            "timestamp": "2026-02-02T10:00:00Z"
                        }
                    ],
                    "count": 1,
                    "total": 10
                }
            }
        )
    },
    tags=['Chat History']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_chat_history(request, room_name):
    """
    Get chat message history for a specific room with pagination.
    """
    try:
        limit = int(request.GET.get('limit', 50))
        offset = int(request.GET.get('offset', 0))
        
        # Fetch messages for the room
        messages = ChatMessage.objects.filter(
            room_name=room_name
        ).select_related('user').order_by('-timestamp')[offset:offset+limit]
        
        # Serialize messages
        message_data = [
            {
                'id': msg.id,
                'user_id': msg.user.id if msg.user else None,
                'user_email': msg.user.email if msg.user else None,
                'username': msg.user_name,
                'message': msg.message,
                'timestamp': msg.timestamp.isoformat()
            }
            for msg in messages
        ]
        
        # Reverse to get chronological order
        message_data.reverse()
        
        return Response({
            'room_name': room_name,
            'messages': message_data,
            'count': len(message_data),
            'total': ChatMessage.objects.filter(room_name=room_name).count()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='delete',
    operation_description="Delete all chat history for a specific room (requires authentication)",
    manual_parameters=[
        openapi.Parameter(
            'room_name',
            openapi.IN_PATH,
            description="Name of the chat room",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description="Chat history deleted successfully",
            examples={
                "application/json": {
                    "message": "Successfully deleted 10 messages from general",
                    "deleted_count": 10
                }
            }
        ),
        401: "Unauthorized - authentication required"
    },
    tags=['Chat History']
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_chat_history(request, room_name):
    """
    Delete all chat messages for a specific room.
    Requires authentication.
    """
    try:
        deleted_count = ChatMessage.objects.filter(room_name=room_name).delete()[0]
        
        return Response({
            'message': f'Successfully deleted {deleted_count} messages from {room_name}',
            'deleted_count': deleted_count
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# WEBSOCKET CONNECTION INFO API
# ============================================================================

@swagger_auto_schema(
    method='get',
    operation_description="Get WebSocket connection information for a chat room",
    manual_parameters=[
        openapi.Parameter(
            'room_name',
            openapi.IN_PATH,
            description="Name of the chat room",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description="WebSocket connection info",
            examples={
                "application/json": {
                    "room_name": "general",
                    "websocket_url": "ws://localhost:8000/ws/chat/general/",
                    "connection_info": {
                        "protocol": "ws",
                        "host": "localhost:8000",
                        "path": "/ws/chat/general/"
                    }
                }
            }
        )
    },
    tags=['WebSocket']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_websocket_info(request, room_name):
    """
    Get WebSocket connection information for a specific chat room.
    """
    try:
        ws_scheme = 'wss' if request.is_secure() else 'ws'
        host = request.get_host()
        ws_path = f'/ws/chat/{room_name}/'
        ws_url = f'{ws_scheme}://{host}{ws_path}'
        
        return Response({
            'room_name': room_name,
            'websocket_url': ws_url,
            'connection_info': {
                'protocol': ws_scheme,
                'host': host,
                'path': ws_path
            },
            'message_format': {
                'send': {
                    'message': 'Your message here',
                    'username': 'your_username',
                    'user_id': 'optional_user_id'
                },
                'receive': {
                    'type': 'chat_message',
                    'message': 'Message content',
                    'username': 'sender_username',
                    'timestamp': 'ISO format timestamp'
                }
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
