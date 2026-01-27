"""
WebSocket Consumers Module

This module contains various WebSocket consumer classes that handle real-time
communication between clients and the server. Each consumer handles different
types of real-time communication scenarios.

Key Concepts:
- Consumer: A class that handles WebSocket connections
- Channels: Groups of connections that can receive messages
- Async/Await: Asynchronous operations for handling concurrent connections

Documentation:
- Consumers: https://channels.readthedocs.io/en/stable/topics/consumers.html
- Channels Groups: https://channels.readthedocs.io/en/stable/topics/channel_layers.html

Author: WebSocket Demo Project
Date: 2025
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

# Configure logging for debugging
logger = logging.getLogger(__name__)

# ============================================================================
# CHAT CONSUMER - Multi-user Chat Room Example
# ============================================================================
# This consumer demonstrates a multi-user chat room where multiple users
# can connect to the same room and exchange messages in real-time.
# ============================================================================

class ChatConsumer(AsyncWebsocketConsumer):
    """
    AsyncWebsocketConsumer for handling chat room connections.
    
    Features:
    - Multiple users can join the same chat room
    - Messages are broadcast to all users in the room
    - User join/leave notifications
    - Real-time message updates
    
    WebSocket Message Format:
    {
        'type': 'chat_message',
        'message': 'Hello World',
        'username': 'john_doe'
    }
    """
    
    async def connect(self):
        """
        Called when a WebSocket connection is established.
        
        Actions:
        1. Extract room name from URL parameter
        2. Add connection to a channel group (room)
        3. Accept the WebSocket connection
        4. Send notification to other users
        """
        # Extract room name from WebSocket URL
        # URL format: ws://localhost/ws/chat/{room_name}/
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        
        # Create a unique group name for the room
        # Format: chat_{room_name}
        self.room_group_name = f'chat_{self.room_name}'
        
        # Add this connection to the room group
        # This allows us to send messages to all users in this room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Accept the WebSocket connection
        await self.accept()
        
        # Log connection
        logger.info(f"User connected to room: {self.room_name}")
        
        # Notify other users that someone joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'message': f'A user joined the room',
                'room': self.room_name
            }
        )
    
    async def disconnect(self, close_code):
        """
        Called when a WebSocket connection is closed.
        
        Actions:
        1. Remove connection from the channel group
        2. Notify other users about disconnection
        3. Clean up resources
        """
        # Notify others before removing from group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'message': 'A user left the room'
            }
        )
        
        # Remove this connection from the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        logger.info(f"User disconnected from room: {self.room_name}")
    
    async def receive(self, text_data):
        """
        Called when the server receives a message from the client.
        
        Actions:
        1. Parse incoming JSON message
        2. Validate message content
        3. Broadcast message to all users in the room
        
        Args:
            text_data (str): JSON-encoded message from client
        """
        try:
            # Parse incoming JSON message
            data = json.loads(text_data)
            message = data.get('message', '')
            username = data.get('username', 'Anonymous')
            
            # Validate message
            if not message or len(message) > 1000:
                await self.send(json.dumps({
                    'type': 'error',
                    'message': 'Invalid message'
                }))
                return
            
            # Broadcast message to all users in the room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username,
                    'timestamp': __import__('datetime').datetime.now().isoformat()
                }
            )
            
            logger.debug(f"Message received from {username}: {message}")
            
        except json.JSONDecodeError:
            # Handle invalid JSON
            await self.send(json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Error in receive: {str(e)}")
            await self.send(json.dumps({
                'type': 'error',
                'message': 'Server error occurred'
            }))
    
    async def chat_message(self, event):
        """
        Handler for 'chat_message' type events.
        
        This method is called when a 'chat_message' event is sent to the group.
        It sends the message to the client who is connected to this consumer.
        
        Args:
            event (dict): Event data containing message details
        """
        # Extract message and send to WebSocket client
        message = event['message']
        username = event['username']
        timestamp = event.get('timestamp', '')
        
        # Send message to WebSocket client
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'username': username,
            'timestamp': timestamp
        }))
    
    async def user_joined(self, event):
        """Handler for user join notifications."""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': event['message'],
            'event': 'user_joined'
        }))
    
    async def user_left(self, event):
        """Handler for user disconnect notifications."""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': event['message'],
            'event': 'user_left'
        }))


# ============================================================================
# NOTIFICATION CONSUMER - Real-time Notifications Example
# ============================================================================
# This consumer demonstrates sending real-time notifications to connected users.
# Useful for alerts, updates, and system notifications.
# ============================================================================

class NotificationConsumer(AsyncWebsocketConsumer):
    """
    AsyncWebsocketConsumer for sending real-time notifications.
    
    Features:
    - Real-time notifications from server to client
    - Multiple notification channels
    - Status updates
    - System alerts
    
    Use Cases:
    - User action notifications
    - System alerts
    - Real-time updates
    - Admin notifications
    """
    
    async def connect(self):
        """
        Accept WebSocket connection and add to notification group.
        """
        # Get user ID from query parameters or session
        self.user_id = self.scope.get('query_string', b'').decode()
        
        # Create group name for this user's notifications
        self.notification_group = f'notifications_{self.user_id or "public"}'
        
        # Add to notification group
        await self.channel_layer.group_add(
            self.notification_group,
            self.channel_name
        )
        
        # Accept connection
        await self.accept()
        
        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'connection_status',
            'status': 'connected',
            'message': 'Successfully connected to notifications',
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }))
        
        logger.info(f"Notification consumer connected for user: {self.user_id}")
    
    async def disconnect(self, close_code):
        """
        Remove from notification group on disconnect.
        """
        await self.channel_layer.group_discard(
            self.notification_group,
            self.channel_name
        )
        logger.info(f"Notification consumer disconnected for user: {self.user_id}")
    
    async def send_notification(self, event):
        """
        Handler to send notifications to client.
        
        Args:
            event (dict): Event containing notification data
        """
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'title': event.get('title', ''),
            'message': event.get('message', ''),
            'priority': event.get('priority', 'normal'),
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }))


# ============================================================================
# COUNTER CONSUMER - Real-time Counter Example
# ============================================================================
# This consumer demonstrates real-time synchronized counter across all users.
# Useful for tracking active users, live statistics, etc.
# ============================================================================

class CounterConsumer(AsyncWebsocketConsumer):
    """
    AsyncWebsocketConsumer for real-time counter synchronization.
    
    Features:
    - Real-time counter updates to all connected clients
    - Counter increment/decrement
    - Synchronized state across all users
    
    Use Cases:
    - Active user count
    - Live statistics
    - Real-time metrics
    - Stock ticker updates
    """
    
    counter_group = 'global_counter'  # Group name for counter
    
    async def connect(self):
        """
        Connect to counter group and send current counter value.
        """
        # Add to global counter group
        await self.channel_layer.group_add(
            self.counter_group,
            self.channel_name
        )
        
        # Accept connection
        await self.accept()
        
        # Send initial counter value
        await self.send(text_data=json.dumps({
            'type': 'counter_update',
            'counter': 0,
            'message': 'Connected to counter'
        }))
        
        # Notify others about new connection
        await self.channel_layer.group_send(
            self.counter_group,
            {
                'type': 'user_count_update',
                'count': 1
            }
        )
    
    async def disconnect(self, close_code):
        """
        Remove from counter group on disconnect.
        """
        await self.channel_layer.group_discard(
            self.counter_group,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """
        Handle counter operations (increment, decrement, reset).
        
        Message format:
        {
            'action': 'increment',  # or 'decrement', 'reset'
            'value': 1
        }
        """
        try:
            data = json.loads(text_data)
            action = data.get('action', 'increment')
            value = data.get('value', 1)
            
            # Broadcast counter update to all connected clients
            await self.channel_layer.group_send(
                self.counter_group,
                {
                    'type': 'counter_update',
                    'action': action,
                    'value': value
                }
            )
            
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
    
    async def counter_update(self, event):
        """
        Handler for counter update events.
        """
        await self.send(text_data=json.dumps({
            'type': 'counter_update',
            'action': event.get('action', 'update'),
            'value': event.get('value', 0),
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }))
    
    async def user_count_update(self, event):
        """
        Handler for user count updates.
        """
        await self.send(text_data=json.dumps({
            'type': 'user_count_update',
            'count': event.get('count', 0)
        }))
