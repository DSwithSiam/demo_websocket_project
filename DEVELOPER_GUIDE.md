# 👨‍💻 Developer Guide - Contributing & Extending

Guide for developers who want to understand, modify, and extend the WebSocket project.

---

## 📋 Project Structure for Developers

```
demo_websocket_project/
├── consumers.py          ← START HERE: Main WebSocket logic
├── routing.py            ← WebSocket URL mapping
├── views.py              ← HTTP views
├── urls.py               ← HTTP URL routing
├── asgi.py               ← ASGI config (don't modify unless needed)
│
└── templates/core/
    ├── base.html         ← Common CSS & utilities
    ├── chat_room.html    ← Chat JS implementation
    ├── notifications.html ← Notifications JS
    └── counter.html      ← Counter JS
```

---

## 🔍 Understanding the Flow

### How a WebSocket Connection Works

```
1. Browser loads http://localhost:8000/chat/room/general/
   ↓
2. Django view (views.py) renders chat_room.html
   ↓
3. JavaScript in template connects to WebSocket:
   new WebSocket('ws://localhost:8000/ws/chat/general/')
   ↓
4. Django ASGI (asgi.py) routes to ChatConsumer (consumers.py)
   ↓
5. ChatConsumer.connect() is called
   - Consumer joins channel group
   - Accepts connection
   ↓
6. Browser sends message via WebSocket
   ↓
7. ChatConsumer.receive() is called
   - Parses message
   - Broadcasts to group
   ↓
8. Channel layer sends to all in group
   ↓
9. All ChatConsumer instances receive group message
   ↓
10. Each consumer calls chat_message() handler
    - Sends to their client
    ↓
11. JavaScript receives message
    - Updates UI
```

---

## 🏗️ Creating a New Feature

### Step 1: Plan Your Consumer

```python
# What does it need to do?
# - Connect users?
# - Broadcast messages?
# - Handle specific events?
# - Store data?

# Example: Real-time document editing
class DocumentConsumer(AsyncWebsocketConsumer):
    """
    Handles real-time collaborative document editing.
    Multiple users can edit same document.
    Changes broadcast to all viewers.
    """
```

### Step 2: Create the Consumer

```python
# core/consumers.py

class DocumentConsumer(AsyncWebsocketConsumer):
    """Real-time document collaboration."""
    
    async def connect(self):
        """Connect to document editing group."""
        self.doc_id = self.scope['url_route']['kwargs']['doc_id']
        self.doc_group = f'doc_{self.doc_id}'
        
        # Join group
        await self.channel_layer.group_add(
            self.doc_group,
            self.channel_name
        )
        
        # Accept connection
        await self.accept()
        
        # Notify others
        await self.channel_layer.group_send(
            self.doc_group,
            {'type': 'user_joined'}
        )
    
    async def disconnect(self, close_code):
        """Handle disconnect."""
        await self.channel_layer.group_discard(
            self.doc_group,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming changes."""
        data = json.loads(text_data)
        
        # Broadcast change to all users
        await self.channel_layer.group_send(
            self.doc_group,
            {
                'type': 'content_changed',
                'content': data['content'],
                'user': data['user']
            }
        )
    
    async def content_changed(self, event):
        """Handle content change event."""
        await self.send(text_data=json.dumps({
            'type': 'content_changed',
            'content': event['content'],
            'user': event['user']
        }))
    
    async def user_joined(self, event):
        """Handle user joined event."""
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'message': 'Someone joined'
        }))
```

### Step 3: Add to Routing

```python
# core/routing.py

from django.urls import re_path
from core import consumers

websocket_urlpatterns = [
    # ... existing patterns ...
    
    # New endpoint
    re_path(
        r'ws/document/(?P<doc_id>\w+)/$',
        consumers.DocumentConsumer.as_asgi()
    ),
]
```

### Step 4: Create Django View

```python
# core/views.py

def document_editor(request, doc_id):
    """Display document editor."""
    context = {
        'doc_id': doc_id,
        'page_title': f'Editing: {doc_id}',
        'ws_scheme': 'wss' if request.is_secure() else 'ws',
        'host': request.get_host(),
    }
    return render(request, 'core/document_editor.html', context)
```

### Step 5: Add URL Route

```python
# core/urls.py

urlpatterns = [
    # ... existing paths ...
    
    path(
        'document/<str:doc_id>/',
        views.document_editor,
        name='document_editor'
    ),
]
```

### Step 6: Create Template

```html
<!-- core/templates/core/document_editor.html -->

{% extends 'core/base.html' %}

{% block title %}Document Editor - {{ doc_id }}{% endblock %}

{% block content %}
<div class="container">
    <h1>Document: {{ doc_id }}</h1>
    <textarea id="editor" style="width: 100%; height: 500px;"></textarea>
</div>

<script>
    const docSocket = new WebSocket(
        `{{ ws_scheme }}://{{ host }}/ws/document/{{ doc_id }}/`
    );

    const editor = document.getElementById('editor');

    // Send changes
    editor.addEventListener('change', function() {
        docSocket.send(JSON.stringify({
            type: 'content_changed',
            content: editor.value,
            user: 'me'
        }));
    });

    // Receive changes
    docSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        if (data.type === 'content_changed') {
            editor.value = data.content;
        }
    };
</script>
{% endblock %}
```

---

## 🧪 Testing Your Consumer

### Unit Test Example

```python
# core/tests.py

from channels.testing import WebsocketCommunicator
from core.consumers import ChatConsumer
import json
import pytest

@pytest.mark.asyncio
async def test_chat_consumer_connect():
    """Test chat consumer connection."""
    communicator = WebsocketCommunicator(
        ChatConsumer.as_asgi(),
        '/ws/chat/test_room/'
    )
    
    # Connect
    connected, subprotocol = await communicator.connect()
    assert connected
    
    # Disconnect
    await communicator.disconnect()

@pytest.mark.asyncio
async def test_chat_message():
    """Test sending and receiving messages."""
    communicator = WebsocketCommunicator(
        ChatConsumer.as_asgi(),
        '/ws/chat/test_room/'
    )
    
    await communicator.connect()
    
    # Send message
    await communicator.send_json_to({
        'type': 'chat_message',
        'message': 'Hello',
        'username': 'Test'
    })
    
    # Receive message
    response = await communicator.receive_json_from()
    assert response['message'] == 'Hello'
    
    await communicator.disconnect()
```

### Integration Test Example

```python
# Test with actual WebSocket

import asyncio
import websockets
import json

async def test_integration():
    """Test WebSocket integration."""
    # Connect two clients
    async with websockets.connect('ws://localhost:8000/ws/chat/test_room/') as client1:
        async with websockets.connect('ws://localhost:8000/ws/chat/test_room/') as client2:
            
            # Send from client1
            await client1.send(json.dumps({
                'type': 'chat_message',
                'message': 'Hello',
                'username': 'User1'
            }))
            
            # Receive on client2
            message = await client2.recv()
            data = json.loads(message)
            assert data['message'] == 'Hello'

# Run test
asyncio.run(test_integration())
```

---

## 🐛 Debugging Tips

### Enable Logging

```python
# settings.py

LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

### Log in Consumer

```python
import logging

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def receive(self, text_data):
        logger.debug(f'Received: {text_data}')
        try:
            # ... process message ...
        except Exception as e:
            logger.error(f'Error: {str(e)}')
```

### Browser DevTools

```javascript
// In browser console
socket.onmessage = function(e) {
    console.log('Received:', e.data);
    const data = JSON.parse(e.data);
    console.table(data);
};

// Monitor connection
socket.onopen = () => console.log('Connected');
socket.onclose = () => console.log('Disconnected');
socket.onerror = (e) => console.error('Error:', e);
```

---

## 📊 Performance Optimization

### 1. Connection Pooling

```python
# Reuse connections instead of creating new ones
class OptimizedConsumer(AsyncWebsocketConsumer):
    # Use connection pooling for database
    pass
```

### 2. Message Batching

```python
# Instead of sending many small messages, batch them
async def send_batched_messages(self, messages, batch_size=10):
    for i in range(0, len(messages), batch_size):
        batch = messages[i:i + batch_size]
        await self.send(json.dumps({
            'type': 'batch',
            'messages': batch
        }))
```

### 3. Selective Broadcasting

```python
# Only send to users who care about the change
async def selective_broadcast(self, event_type, target_users):
    for user in target_users:
        await self.channel_layer.group_send(
            f'user_{user}',
            {
                'type': event_type,
                'data': {...}
            }
        )
```

### 4. Caching

```python
# Cache frequently accessed data
from functools import lru_cache

@lru_cache(maxsize=128)
async def get_room_info(room_id):
    # Get room from cache or database
    pass
```

---

## 🔐 Security Considerations

### 1. Input Validation

```python
def validate_message(message):
    """Validate user message."""
    if not message or len(message) > 1000:
        raise ValueError('Invalid message')
    
    # Check for malicious content
    if '<script>' in message.lower():
        raise ValueError('Script tags not allowed')
    
    return message
```

### 2. Authentication

```python
async def connect(self):
    # Check if user is authenticated
    if not self.scope['user'].is_authenticated:
        await self.close()
        return
    
    await self.accept()
```

### 3. Authorization

```python
async def receive(self, text_data):
    data = json.loads(text_data)
    user = self.scope['user']
    
    # Check permissions
    if not user.has_perm('can_send_messages'):
        await self.send_error('Permission denied')
        return
    
    # Process message
```

### 4. Rate Limiting

```python
from datetime import datetime, timedelta

class RateLimitedConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.messages = []
    
    async def check_rate_limit(self):
        now = datetime.now()
        # Remove old messages (older than 1 minute)
        self.messages = [
            m for m in self.messages
            if (now - m).seconds < 60
        ]
        
        # Check limit (100 per minute)
        if len(self.messages) >= 100:
            return False
        
        self.messages.append(now)
        return True
```

---

## 🚀 Advanced Patterns

### Pattern 1: Presence System

```python
class PresenceConsumer(AsyncWebsocketConsumer):
    """Track who's online."""
    
    async def connect(self):
        await self.channel_layer.group_add('presence', self.channel_name)
        
        # Tell everyone I'm online
        await self.channel_layer.group_send('presence', {
            'type': 'user_online',
            'user': self.scope['user'].username
        })
        
        await self.accept()
    
    async def user_online(self, event):
        await self.send_json(event)
```

### Pattern 2: Event Sourcing

```python
# Store all events for audit trail
class EventSourcedConsumer(AsyncWebsocketConsumer):
    async def receive(self, text_data):
        data = json.loads(text_data)
        
        # Save event
        event = Event.objects.create(
            user=self.scope['user'],
            type=data['type'],
            data=data
        )
        
        # Broadcast
        await self.broadcast_event(event)
```

### Pattern 3: RPC-like Pattern

```python
class RPCConsumer(AsyncWebsocketConsumer):
    """Remote procedure call pattern."""
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        method = data.get('method')
        params = data.get('params', {})
        call_id = data.get('id')
        
        try:
            # Call method
            result = await getattr(self, method)(**params)
            
            # Send response
            await self.send_json({
                'id': call_id,
                'result': result
            })
        except Exception as e:
            await self.send_json({
                'id': call_id,
                'error': str(e)
            })
    
    async def get_users(self):
        """Example RPC method."""
        return list(User.objects.values('id', 'username'))
```

---

## 🔧 Troubleshooting Guide

### Consumer not receiving messages

```python
# Check 1: Is consumer added to group?
await self.channel_layer.group_add(group_name, self.channel_name)

# Check 2: Is message type handler defined?
async def message_type_name(self, event):
    await self.send(...)

# Check 3: Is group name correct in group_send?
await self.channel_layer.group_send(
    'correct_group_name',  # Check spelling!
    {'type': 'message_type_name'}
)
```

### Connection dropping

```python
# Implement reconnection logic
socket.onclose = function(e) {
    console.log('Connection closed');
    // Try to reconnect after 3 seconds
    setTimeout(connectWebSocket, 3000);
};
```

### Memory leaks

```python
# Always cleanup on disconnect
async def disconnect(self, close_code):
    # Remove from all groups
    await self.channel_layer.group_discard(
        self.group_name,
        self.channel_name
    )
```

---

## 🎓 Learning Resources

### Code to Study

1. **consumers.py** - How to create consumers
2. **chat_room.html** - JavaScript WebSocket client
3. **routing.py** - URL routing
4. **asgi.py** - ASGI configuration

### External Resources

- [Channels Documentation](https://channels.readthedocs.io/)
- [Django Async Views](https://docs.djangoproject.com/en/stable/topics/async/)
- [WebSocket Examples](https://github.com/django/channels/tree/main/examples)

---

## 📝 Checklist for Adding Features

- [ ] Create consumer class
- [ ] Add to routing.py
- [ ] Create/update Django view
- [ ] Add URL pattern
- [ ] Create template with JavaScript
- [ ] Test WebSocket connection
- [ ] Handle errors
- [ ] Add logging
- [ ] Write tests
- [ ] Document with comments
- [ ] Update README if needed

---

**Happy Development! 🚀**
