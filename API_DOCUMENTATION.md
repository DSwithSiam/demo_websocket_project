# 📡 WebSocket API Documentation

Complete reference for all WebSocket endpoints and message formats.

---

## 🔗 WebSocket Endpoints

### Base URL
```
ws://localhost:8000/ws/
```

---

## 1. Chat Consumer

### Endpoint
```
ws://localhost:8000/ws/chat/{room_name}/
```

### Parameters
- `room_name` (string, required): Name of the chat room

### Example URLs
```
ws://localhost:8000/ws/chat/general/
ws://localhost:8000/ws/chat/tech/
ws://localhost:8000/ws/chat/random/
```

### Client → Server Messages

#### Send Chat Message
```json
{
    "type": "chat_message",
    "message": "Hello everyone!",
    "username": "john_doe"
}
```

**Validation:**
- `message`: Required, max 1000 characters
- `username`: Optional, defaults to "Anonymous"

### Server → Client Messages

#### Chat Message (Broadcast)
```json
{
    "type": "chat_message",
    "message": "Hello everyone!",
    "username": "john_doe",
    "timestamp": "2025-01-27T12:30:45.123456"
}
```

#### User Joined
```json
{
    "type": "notification",
    "message": "A user joined the room",
    "event": "user_joined"
}
```

#### User Left
```json
{
    "type": "notification",
    "message": "A user left the room",
    "event": "user_left"
}
```

#### Error
```json
{
    "type": "error",
    "message": "Invalid message format"
}
```

### JavaScript Implementation

```javascript
// Connect
const socket = new WebSocket(`ws://localhost:8000/ws/chat/general/`);

// Handle messages
socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    if (data.type === 'chat_message') {
        console.log(`${data.username}: ${data.message}`);
    }
    else if (data.type === 'notification') {
        console.log(data.message);
    }
};

// Send message
socket.send(JSON.stringify({
    type: 'chat_message',
    message: 'Hello!',
    username: 'John'
}));
```

### Python Implementation (Django View)

```python
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_chat_message(room_name, message, username='System'):
    channel_layer = get_channel_layer()
    
    async_to_sync(channel_layer.group_send)(
        f'chat_{room_name}',
        {
            'type': 'chat_message',
            'message': message,
            'username': username,
            'timestamp': str(datetime.now().isoformat())
        }
    )
```

---

## 2. Notification Consumer

### Endpoint
```
ws://localhost:8000/ws/notifications/
```

### Connection Initialization

**Server → Client (Connection Established)**
```json
{
    "type": "connection_status",
    "status": "connected",
    "message": "Successfully connected to notifications",
    "timestamp": "2025-01-27T12:30:45.123456"
}
```

### Server → Client Messages

#### Notification
```json
{
    "type": "notification",
    "title": "New Message",
    "message": "You have a new message from John",
    "priority": "normal",
    "timestamp": "2025-01-27T12:30:45.123456"
}
```

**Priority Levels:**
- `low`: Info notifications
- `normal`: Regular notifications (default)
- `high`: Urgent alerts

#### Connection Status
```json
{
    "type": "connection_status",
    "status": "connected",
    "message": "Connection established"
}
```

### JavaScript Implementation

```javascript
// Connect
const notifSocket = new WebSocket(`ws://localhost:8000/ws/notifications/`);

// Handle notifications
notifSocket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    if (data.type === 'notification') {
        // Show notification
        showNotification(
            data.title,
            data.message,
            data.priority
        );
    }
};

// Display notification
function showNotification(title, message, priority) {
    const badge = priority === 'high' ? '⚠️ ' : 'ℹ️ ';
    console.log(`${badge}${title}: ${message}`);
}
```

### Python Implementation (Send Notification)

```python
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import datetime

def send_user_notification(user_id, title, message, priority='normal'):
    channel_layer = get_channel_layer()
    
    async_to_sync(channel_layer.group_send)(
        f'notifications_{user_id}',
        {
            'type': 'send_notification',
            'title': title,
            'message': message,
            'priority': priority,
            'timestamp': datetime.datetime.now().isoformat()
        }
    )

# Usage
send_user_notification(
    user_id=123,
    title='New Order',
    message='Order #456 has been received',
    priority='high'
)
```

---

## 3. Counter Consumer

### Endpoint
```
ws://localhost:8000/ws/counter/
```

### Connection Initialization

**Server → Client (Connection Established)**
```json
{
    "type": "counter_update",
    "counter": 0,
    "message": "Connected to counter"
}
```

### Client → Server Messages

#### Increment Counter
```json
{
    "action": "increment",
    "value": 1
}
```

#### Decrement Counter
```json
{
    "action": "decrement",
    "value": 1
}
```

#### Reset Counter
```json
{
    "action": "reset",
    "value": 0
}
```

#### Set Custom Value
```json
{
    "action": "increment",
    "value": 5
}
```

### Server → Client Messages

#### Counter Update (Broadcast)
```json
{
    "type": "counter_update",
    "action": "increment",
    "value": 1,
    "timestamp": "2025-01-27T12:30:45.123456"
}
```

#### User Count Update
```json
{
    "type": "user_count_update",
    "count": 3
}
```

### JavaScript Implementation

```javascript
// Connect
let counter = 0;
const counterSocket = new WebSocket(`ws://localhost:8000/ws/counter/`);

// Handle updates
counterSocket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    if (data.type === 'counter_update') {
        // Update counter based on action
        switch(data.action) {
            case 'increment':
                counter += data.value;
                break;
            case 'decrement':
                counter -= data.value;
                break;
            case 'reset':
                counter = 0;
                break;
        }
        updateDisplay();
    }
};

// Send increment
function increment() {
    counterSocket.send(JSON.stringify({
        action: 'increment',
        value: 1
    }));
}

// Send decrement
function decrement() {
    counterSocket.send(JSON.stringify({
        action: 'decrement',
        value: 1
    }));
}

// Send reset
function reset() {
    counterSocket.send(JSON.stringify({
        action: 'reset',
        value: 0
    }));
}

function updateDisplay() {
    document.getElementById('counter').textContent = counter;
}
```

### Python Implementation

```python
def broadcast_counter_update(action, value):
    channel_layer = get_channel_layer()
    
    async_to_sync(channel_layer.group_send)(
        'global_counter',
        {
            'type': 'counter_update',
            'action': action,
            'value': value,
            'timestamp': datetime.datetime.now().isoformat()
        }
    )
```

---

## 📝 HTTP API Endpoints

### Send Notification (HTTP)

#### Endpoint
```
POST /api/notifications/send/
```

#### Request Body
```json
{
    "title": "New Message",
    "message": "You have a new message",
    "priority": "normal"
}
```

#### Response (Success)
```json
{
    "status": "success",
    "message": "Notification sent",
    "data": {
        "title": "New Message",
        "message": "You have a new message",
        "priority": "normal"
    }
}
```

#### Response (Error)
```json
{
    "status": "error",
    "message": "Title and message are required"
}
```

#### cURL Example
```bash
curl -X POST http://localhost:8000/api/notifications/send/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test",
    "message": "Hello!",
    "priority": "high"
  }'
```

#### JavaScript Example
```javascript
async function sendNotification() {
    const response = await fetch('/api/notifications/send/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            title: 'New Alert',
            message: 'Important update!',
            priority: 'high'
        })
    });
    
    const result = await response.json();
    console.log(result);
}
```

---

## 🔐 Authentication

### WebSocket Authentication

```python
# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.auth import get_user

class AuthenticatedConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = await get_user(self.scope)
        
        if self.user is None:
            # Reject connection if not authenticated
            await self.close()
        else:
            await self.accept()
```

### Using Token Authentication

```javascript
// Get token from storage
const token = localStorage.getItem('auth_token');

// Include in WebSocket URL or headers
const socket = new WebSocket(
    `ws://localhost:8000/ws/chat/general/?token=${token}`
);
```

---

## ⚠️ Error Handling

### Common Errors

#### Invalid JSON
```json
{
    "type": "error",
    "message": "Invalid JSON format"
}
```

#### Message Too Long
```json
{
    "type": "error",
    "message": "Invalid message (max 1000 characters)"
}
```

#### Connection Lost
```
Error Code: 1006
Reason: Abnormal Closure
```

### Error Handling Example

```javascript
socket.onerror = function(error) {
    console.error('WebSocket error:', error);
    // Reconnect logic
    setTimeout(reconnect, 3000);
};

socket.onclose = function(e) {
    if (e.wasClean) {
        console.log('Connection closed normally');
    } else {
        console.error('Connection lost');
        setTimeout(reconnect, 3000);
    }
};
```

---

## 📊 Testing the API

### Using WebSocket CLI Tool

```bash
# Install wscat
npm install -g wscat

# Connect to chat
wscat -c ws://localhost:8000/ws/chat/general/

# Send message
{"type": "chat_message", "message": "Hello", "username": "Test"}

# Receive messages in real-time
```

### Using Python

```python
import asyncio
import websockets
import json

async def test_chat():
    async with websockets.connect('ws://localhost:8000/ws/chat/general/') as ws:
        # Send message
        await ws.send(json.dumps({
            'type': 'chat_message',
            'message': 'Hello from Python',
            'username': 'PythonBot'
        }))
        
        # Receive response
        response = await ws.recv()
        print(response)

asyncio.run(test_chat())
```

---

## 🔄 Message Flow Examples

### Complete Chat Flow

```
Client 1                              Server                    Client 2
   │                                    │                          │
   ├─────── WebSocket Connect ────────→ │                          │
   │                                    │ Accept Connection        │
   │ ←───────────── Accept ─────────── │                          │
   │                                    │                          │
   │                                    │ ← WebSocket Connect ─ ─ →
   │                                    │                          │
   │                                    │ Accept Connection        │
   │                                    │ ─────── Accept ────→     │
   │                                    │                          │
   │─ Send Chat Message ───────────────→ │                          │
   │                                    │ Broadcast to group       │
   │ ←─── Receive Message ─────────── │ ─────────────────→ Receive
   │                                    │                          │
   │ ← User 2 Joined Notification ────  │ ← Receive Message ───   │
   │                                    │                          │
   │─ Send Chat Message ───────────────→ │                          │
   │                                    │ Broadcast to group       │
   │ ←─── Receive Message ─────────── │ ←─────────── Receive   ─→ │
   │                                    │                          │
```

---

## 🎯 Rate Limiting

### Current Limitations

- No built-in rate limiting
- Max message length: 1000 characters
- Per-connection message limit: None

### Recommended Implementation

```python
# Add to consumer
from datetime import datetime, timedelta

class RateLimitedConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.messages_count = 0
        self.last_reset = datetime.now()
    
    async def receive(self, text_data):
        now = datetime.now()
        
        # Reset counter every minute
        if (now - self.last_reset).seconds > 60:
            self.messages_count = 0
            self.last_reset = now
        
        # Check rate limit (max 100 messages per minute)
        if self.messages_count >= 100:
            await self.send(json.dumps({
                'type': 'error',
                'message': 'Rate limit exceeded'
            }))
            return
        
        self.messages_count += 1
        # Process message...
```

---

## 📞 Support

For API questions or issues:
1. Check inline code comments
2. Review README.md
3. See error handling section
4. Check Django Channels docs

---

**Last Updated:** January 27, 2025
**API Version:** 1.0
