# 🔌 WebSocket Demo Project - Complete Documentation

A comprehensive Django + Django Channels WebSocket implementation with real-time chat, notifications, and synchronized counter examples.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [Installation & Setup](#installation--setup)
5. [Running the Project](#running-the-project)
6. [WebSocket Demos](#websocket-demos)
7. [Architecture](#architecture)
8. [Code Examples](#code-examples)
9. [Deployment](#deployment)
10. [Troubleshooting](#troubleshooting)
11. [Resources](#resources)

---

## 🎯 Overview

This project demonstrates how to implement real-time, bidirectional communication using WebSockets with Django and Django Channels. It provides three complete, production-ready examples:

- **Chat Room**: Multi-user real-time messaging
- **Notifications**: Server-to-client real-time notifications
- **Synchronized Counter**: Real-time state synchronization across users

### Why WebSockets?

Traditional HTTP is request-response based:
```
Client → Request → Server → Response → Client
```

WebSocket provides persistent, bidirectional communication:
```
Client ↔ Server (persistent connection)
```

**Benefits:**
- ✓ Real-time communication
- ✓ Lower latency
- ✓ Reduced bandwidth
- ✓ Better user experience
- ✓ Event-driven architecture

---

## ✨ Features

### 1. Chat Room Demo
- Multi-user chat with room support
- Real-time message broadcasting
- User join/leave notifications
- Message validation
- Scalable channel groups

### 2. Notifications Demo
- Server-to-client real-time notifications
- Priority levels (low, normal, high)
- User-specific notifications
- Connection status indicator
- Test notification endpoint

### 3. Counter Demo
- Synchronized counter across all users
- Increment/decrement/reset operations
- Activity tracking
- User count display
- Real-time synchronization

### All Demos Include:
- ✓ Full error handling
- ✓ Connection status monitoring
- ✓ Detailed logging
- ✓ Responsive UI
- ✓ Inline documentation
- ✓ Modern Bootstrap UI

---

## 📁 Project Structure

```
demo_websocket_project/
├── demo_websocket_project/        # Main project configuration
│   ├── __init__.py
│   ├── asgi.py                   # ⭐ ASGI configuration with WebSocket support
│   ├── settings.py               # Project settings
│   ├── urls.py                   # Main URL routing
│   ├── wsgi.py                   # WSGI configuration
│   └── __pycache__/
│
├── core/                          # Core app with WebSocket demos
│   ├── __init__.py
│   ├── consumers.py              # ⭐ WebSocket consumer implementations
│   ├── models.py                 # Database models
│   ├── views.py                  # ⭐ HTTP views for rendering pages
│   ├── urls.py                   # Core app URL patterns
│   ├── admin.py
│   ├── apps.py
│   ├── routing.py                # ⭐ WebSocket URL routing
│   ├── tests.py
│   ├── migrations/
│   │   └── __init__.py
│   └── templates/
│       └── core/
│           ├── base.html         # Base template with common styles
│           ├── index.html        # Home page with demo overview
│           ├── chat_room_list.html  # List of available chat rooms
│           ├── chat_room.html    # Single chat room interface
│           ├── notifications.html # Real-time notifications demo
│           └── counter.html      # Synchronized counter demo
│
├── auth/                          # Authentication app
│   ├── migrations/
│   └── ...
│
├── db.sqlite3                     # SQLite database
├── manage.py                      # Django management command
└── README.md                      # This file
```

### Key Files Explained:

| File | Purpose |
|------|---------|
| `asgi.py` | ASGI application routing (HTTP + WebSocket) |
| `consumers.py` | WebSocket consumer classes handling connections |
| `routing.py` | WebSocket URL patterns |
| `views.py` | Django views for rendering HTML pages |
| `urls.py` | HTTP URL routing |

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Create Virtual Environment

```bash
# Navigate to project directory
cd /home/backend/siam/prc/demo_websocket_project

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 2: Install Dependencies

```bash
# Install required packages
pip install django
pip install channels
pip install daphne
pip install djangorestframework
pip install djangorestframework-simplejwt
pip install django-cors-headers
pip install drf-yasg
```

Or use requirements.txt:

```bash
pip install -r requirements.txt
```

### Step 3: Database Migration

```bash
# Apply database migrations
python manage.py migrate

# Create superuser (optional, for admin)
python manage.py createsuperuser
```

### Step 4: Verify Installation

```bash
# Run development server (uses Daphne automatically)
python manage.py runserver
```

Visit: `http://localhost:8000/`

---

## ▶️ Running the Project

### Option 1: Using Django Development Server

```bash
# From project root directory
source venv/bin/activate
python manage.py runserver
```

**Output:**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### Option 2: Using Daphne (ASGI Server)

```bash
# Install daphne first
pip install daphne

# Run Daphne server
daphne -b 0.0.0.0 -p 8000 demo_websocket_project.asgi:application
```

### Option 3: Using Uvicorn

```bash
# Install uvicorn
pip install uvicorn

# Run Uvicorn server
uvicorn demo_websocket_project.asgi:application --host 0.0.0.0 --port 8000
```

### Access the Application

Open your browser and navigate to:

- **Home**: `http://localhost:8000/`
- **Chat Rooms**: `http://localhost:8000/chat/`
- **Notifications**: `http://localhost:8000/notifications/`
- **Counter**: `http://localhost:8000/counter/`

---

## 📱 WebSocket Demos

### 1. Chat Room Demo

#### URL
```
ws://localhost:8000/ws/chat/{room_name}/
```

#### How It Works

1. User connects to a specific chat room
2. All users in same room form a "channel group"
3. Messages are broadcast to all users in the group
4. User join/leave notifications are sent

#### Message Format (Client → Server)

```json
{
    "type": "chat_message",
    "message": "Hello everyone!",
    "username": "john_doe"
}
```

#### Message Format (Server → Client)

```json
{
    "type": "chat_message",
    "message": "Hello everyone!",
    "username": "john_doe",
    "timestamp": "2025-01-27T12:30:45.123456"
}
```

#### JavaScript Example

```javascript
// Connect to chat room
const roomName = 'general';
const chatSocket = new WebSocket(
    `ws://${window.location.host}/ws/chat/${roomName}/`
);

// Handle connection
chatSocket.onopen = function(e) {
    console.log('Connected to chat room');
};

// Receive messages
chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log(data.username + ': ' + data.message);
};

// Send message
chatSocket.send(JSON.stringify({
    type: 'chat_message',
    message: 'Hello!',
    username: 'My Name'
}));

// Handle disconnect
chatSocket.onclose = function(e) {
    console.log('Disconnected from chat room');
};
```

---

### 2. Notifications Demo

#### URL
```
ws://localhost:8000/ws/notifications/
```

#### How It Works

1. Client connects to notifications endpoint
2. Server sends notifications to specific users
3. Multiple notification channels can be created
4. Priority levels supported (low, normal, high)

#### Message Format (Server → Client)

```json
{
    "type": "notification",
    "title": "New Message",
    "message": "You have a new message from John",
    "priority": "high",
    "timestamp": "2025-01-27T12:30:45.123456"
}
```

#### Send Notification Programmatically

```python
# In your Django code, send notification via Channel Layer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

channel_layer = get_channel_layer()

# Send to specific user
async_to_sync(channel_layer.group_send)(
    'notifications_user_123',
    {
        'type': 'send_notification',
        'title': 'New Message',
        'message': 'You have a new notification',
        'priority': 'high'
    }
)
```

#### JavaScript Example

```javascript
// Connect to notifications
const notifSocket = new WebSocket(
    `ws://${window.location.host}/ws/notifications/`
);

// Receive notifications
notifSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    
    // Show notification
    showNotification(
        data.title,
        data.message,
        data.priority
    );
};
```

---

### 3. Counter Demo

#### URL
```
ws://localhost:8000/ws/counter/
```

#### How It Works

1. All users connect to the same counter
2. When counter changes, update is broadcast to all
3. All clients display same synchronized value
4. Activity is tracked and logged

#### Message Format (Client → Server)

```json
{
    "action": "increment",  // or "decrement", "reset"
    "value": 1
}
```

#### Message Format (Server → Client)

```json
{
    "type": "counter_update",
    "action": "increment",
    "value": 1,
    "timestamp": "2025-01-27T12:30:45.123456"
}
```

#### JavaScript Example

```javascript
// Connect to counter
const counterSocket = new WebSocket(
    `ws://${window.location.host}/ws/counter/`
);

// Receive counter updates
counterSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    updateCounterDisplay(data.value);
};

// Send increment
counterSocket.send(JSON.stringify({
    action: 'increment',
    value: 1
}));

// Send decrement
counterSocket.send(JSON.stringify({
    action: 'decrement',
    value: 1
}));

// Reset counter
counterSocket.send(JSON.stringify({
    action: 'reset',
    value: 0
}));
```

---

## 🏗️ Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     ASGI Application                        │
│                  (demo_websocket_project)                   │
└────────────────┬──────────────────────────┬─────────────────┘
                 │                          │
        ┌────────▼─────────┐      ┌─────────▼────────┐
        │   HTTP Handler   │      │  WebSocket Router │
        │   (Django WSGI)  │      │ (Django Channels) │
        └────────┬─────────┘      └────────┬──────────┘
                 │                         │
        ┌────────▼─────────┐      ┌────────▼──────────┐
        │  HTTP Views      │      │ WebSocket Routing │
        │  URL Patterns    │      │  (routing.py)     │
        │  Templates       │      └────────┬──────────┘
        └──────────────────┘               │
                                  ┌────────▼──────────┐
                                  │  Consumers        │
                                  │  - ChatConsumer   │
                                  │  - NotifConsumer  │
                                  │  - CounterConsumer│
                                  └────────┬──────────┘
                                           │
                                  ┌────────▼──────────┐
                                  │ Channel Layers    │
                                  │ (Group Messaging) │
                                  └───────────────────┘
```

### Data Flow

#### Chat Message Flow

```
1. User A sends message
   └─> Client A
       └─> WebSocket Connection
           └─> ChatConsumer.receive()
               └─> channel_layer.group_send()
                   └─> channel_group ('chat_general')
                       └─> All consumers in group
                           └─> Sends to Client A, B, C
```

#### Notification Flow

```
1. Server sends notification
   └─> Signal/API Call
       └─> channel_layer.group_send()
           └─> channel_group ('notifications_user_123')
               └─> NotificationConsumer
                   └─> Sends to Client
```

---

## 💻 Code Examples

### Example 1: Creating a Custom WebSocket Consumer

```python
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class MyCustomConsumer(AsyncWebsocketConsumer):
    """
    Custom WebSocket consumer for real-time features.
    """
    
    async def connect(self):
        """Called when WebSocket connects."""
        # Add to group
        await self.channel_layer.group_add(
            'my_group',
            self.channel_name
        )
        # Accept connection
        await self.accept()
    
    async def disconnect(self, close_code):
        """Called when WebSocket disconnects."""
        # Remove from group
        await self.channel_layer.group_discard(
            'my_group',
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Called when client sends message."""
        data = json.loads(text_data)
        message = data['message']
        
        # Broadcast to group
        await self.channel_layer.group_send(
            'my_group',
            {
                'type': 'chat_message',
                'message': message
            }
        )
    
    async def chat_message(self, event):
        """Called when group sends message."""
        # Send to client
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))
```

### Example 2: Adding to URLs

```python
# core/routing.py
from django.urls import re_path
from core import consumers

websocket_urlpatterns = [
    re_path(r'ws/myfeature/$', consumers.MyCustomConsumer.as_asgi()),
]
```

### Example 3: Sending from Django View

```python
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def my_view(request):
    channel_layer = get_channel_layer()
    
    # Broadcast message to all in group
    async_to_sync(channel_layer.group_send)(
        'my_group',
        {
            'type': 'chat_message',
            'message': 'Hello from Django!'
        }
    )
    
    return JsonResponse({'status': 'ok'})
```

### Example 4: JavaScript Client

```javascript
// Create WebSocket connection
const socket = new WebSocket('ws://localhost:8000/ws/myfeature/');

// Connection opened
socket.onopen = function(e) {
    console.log('WebSocket connection established');
    socket.send(JSON.stringify({
        message: 'Hello Server!'
    }));
};

// Receive message
socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log('Received:', data.message);
};

// Connection closed
socket.onclose = function(e) {
    console.log('WebSocket connection closed');
};

// Error occurred
socket.onerror = function(error) {
    console.error('WebSocket error:', error);
};
```

---

## 🚢 Deployment

### Production Considerations

#### 1. Use a Production ASGI Server

```bash
# Using Daphne
daphne -b 0.0.0.0 -p 8000 -w 4 demo_websocket_project.asgi:application

# Using Uvicorn with Gunicorn
pip install gunicorn uvicorn
gunicorn demo_websocket_project.asgi:application \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
```

#### 2. Configure Channel Layers

For Redis (recommended for production):

```python
# settings.py
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('redis_server', 6379)],
        },
    },
}
```

Install: `pip install channels-redis`

#### 3. Set Environment Variables

```bash
export DEBUG=False
export SECRET_KEY='your-secret-key'
export ALLOWED_HOSTS='yourdomain.com,www.yourdomain.com'
```

#### 4. Use Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 5. SSL/TLS

```nginx
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    # ... rest of configuration
}
```

---

## 🔧 Troubleshooting

### Issue: WebSocket Connection Refused

**Problem:** `WebSocket is closed before the connection is established`

**Solution:**
```bash
# Make sure Daphne server is running
pip install daphne
daphne -b 0.0.0.0 -p 8000 demo_websocket_project.asgi:application
```

### Issue: Messages Not Broadcasting

**Problem:** Messages only appear for sender, not other users

**Solution:**
```python
# Ensure channel layer is configured
# In settings.py
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'  # For development
    }
}
```

### Issue: Static Files Not Loading

**Problem:** CSS/JavaScript not loading

**Solution:**
```bash
# Collect static files
python manage.py collectstatic --noinput
```

### Issue: Database Errors

**Problem:** Migration or database errors

**Solution:**
```bash
# Apply migrations
python manage.py migrate

# Reset database (development only)
python manage.py flush --noinput
python manage.py migrate
```

---

## 📚 Resources

### Documentation Links

- [Django Official Docs](https://docs.djangoproject.com/)
- [Django Channels Documentation](https://channels.readthedocs.io/)
- [WebSocket Protocol RFC 6455](https://tools.ietf.org/html/rfc6455)
- [Mozilla WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

### Additional Resources

- [WebSocket Best Practices](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [Real-time Applications](https://channels.readthedocs.io/en/latest/topics/consumers.html)
- [Channel Layers](https://channels.readthedocs.io/en/latest/topics/channel_layers.html)

### Tutorials

- Creating WebSocket Endpoints
- Broadcasting to Groups
- Authentication with WebSockets
- Scaling WebSocket Applications

---

## 🎓 Learning Path

1. **Beginner:** Understand WebSocket basics
2. **Intermediate:** Run the demos locally
3. **Advanced:** Customize consumers and add new features
4. **Expert:** Deploy to production with proper scaling

---

## 📝 Notes

- This project uses **Django Channels** for WebSocket support
- **In-memory channel layer** is fine for development
- **Redis channel layer** recommended for production
- All code includes detailed comments for learning
- Each demo is self-contained and can be used independently

---

## 💬 Support & Contributions

For questions or issues:
1. Check the troubleshooting section
2. Review the inline code comments
3. Consult the official documentation

---

**Happy WebSocket Development! 🚀**

*Last Updated: January 27, 2025*
*Version: 1.0*
