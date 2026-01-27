# 🚀 Quick Start Guide - WebSocket Demo Project

Get up and running in 5 minutes!

## Step 1: Install Dependencies (1 minute)

```bash
# Navigate to project directory
cd /home/backend/siam/prc/demo_websocket_project

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

## Step 2: Setup Database (30 seconds)

```bash
# Run migrations
python manage.py migrate

# Create admin user (optional)
python manage.py createsuperuser
```

## Step 3: Run Server (30 seconds)

```bash
# Start development server
python manage.py runserver
```

**Output:**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

## Step 4: Access Demos (instant)

Open your browser:

- **Home**: http://localhost:8000/
- **Chat**: http://localhost:8000/chat/
- **Notifications**: http://localhost:8000/notifications/
- **Counter**: http://localhost:8000/counter/

## 💬 Chat Demo - Try It Now

1. Go to: http://localhost:8000/chat/
2. Click "Enter Room" for any room
3. Enter your name
4. Type a message and hit Enter
5. **Open another browser tab** with same room
6. See messages appear in **real-time** on both tabs!

## 🔔 Notifications Demo

1. Go to: http://localhost:8000/notifications/
2. You'll see "Connected" status
3. Scroll down to "Send Test Notification"
4. Fill in title and message
5. Click "Send Test Notification"
6. See notification appear instantly!

## 📊 Counter Demo

1. Go to: http://localhost:8000/counter/
2. See counter display
3. Click Increase/Decrease/Reset buttons
4. **Open another browser tab** with same page
5. Buttons clicked in one tab **instantly update** in other tab!

---

## 📁 File Guide for Developers

### Key Files to Understand

```
consumers.py      - WebSocket connection handlers
├─ ChatConsumer       - Chat room logic
├─ NotificationConsumer - Notification logic
└─ CounterConsumer    - Counter synchronization

routing.py        - WebSocket URL mapping

asgi.py          - Main ASGI config with WebSocket router

views.py         - HTTP views (renders pages)

urls.py          - URL patterns

templates/       - HTML pages with JavaScript
├─ chat_room.html      - Chat interface
├─ notifications.html  - Notification interface
└─ counter.html        - Counter interface
```

---

## 🎯 Understanding the Flow

### Chat Room Example

```
1. User opens http://localhost:8000/chat/room/general/
   ↓
2. Page loads chat_room.html template
   ↓
3. JavaScript creates WebSocket connection
   ws://localhost:8000/ws/chat/general/
   ↓
4. Django routes to ChatConsumer.connect()
   ↓
5. User joins channel group 'chat_general'
   ↓
6. User types message
   ↓
7. JavaScript sends JSON via WebSocket
   ↓
8. ChatConsumer.receive() processes message
   ↓
9. Message broadcast to all in group via channel_layer
   ↓
10. All clients receive message via WebSocket
    ↓
11. JavaScript displays message in chat
```

---

## 💡 Common Tasks

### Add a New WebSocket Endpoint

```python
# Step 1: Create consumer in consumers.py
class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
    
    async def receive(self, text_data):
        await self.send(text_data=json.dumps({
            'message': 'Hello!'
        }))

# Step 2: Add to routing.py
urlpatterns = [
    re_path(r'ws/myendpoint/$', consumers.MyConsumer.as_asgi()),
]

# Step 3: Connect from JavaScript
const socket = new WebSocket('ws://localhost:8000/ws/myendpoint/');
socket.send(JSON.stringify({message: 'Hello'}));
```

### Send Message from Django Code

```python
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def my_view(request):
    channel_layer = get_channel_layer()
    
    async_to_sync(channel_layer.group_send)(
        'chat_general',
        {
            'type': 'chat_message',
            'message': 'Admin message'
        }
    )
    
    return JsonResponse({'sent': True})
```

---

## 🐛 Quick Fixes

### WebSocket Not Connecting

```bash
# Make sure Daphne is installed
pip install daphne

# Verify ASGI setting in manage.py (should be default)
python manage.py runserver
```

### Messages Not Showing

```bash
# Ensure migrations are run
python manage.py migrate

# Restart server
# Ctrl+C then python manage.py runserver
```

### Port Already in Use

```bash
# Use different port
python manage.py runserver 8001
```

---

## 📱 Testing with Multiple Clients

### Method 1: Multiple Browser Tabs
1. Open http://localhost:8000/chat/room/general/
2. Right-click → "Open Link in New Tab"
3. Send message in one tab, see it in another

### Method 2: Multiple Browsers
1. Open Chrome at http://localhost:8000/chat/room/general/
2. Open Firefox at http://localhost:8000/chat/room/general/
3. Send message, see it in both browsers

### Method 3: Curl (for testing)

```bash
# Start counter
python -m websockets ws://localhost:8000/ws/counter/

# Send message in console
> {"action": "increment", "value": 1}
```

---

## 🔑 Important Concepts

### Channel Groups

Think of groups as "broadcast lists":

```python
# Add connection to group
await self.channel_layer.group_add('chat_general', self.channel_name)

# Send message to entire group
await self.channel_layer.group_send('chat_general', {
    'type': 'chat_message',
    'message': 'Hello all!'
})

# Remove from group
await self.channel_layer.group_discard('chat_general', self.channel_name)
```

### Types

The 'type' field tells which method to call:

```python
# Send this:
{'type': 'chat_message', 'message': 'Hello'}

# Calls this method:
async def chat_message(self, event):
    await self.send(...)
```

### Async/Await

All consumer methods are async:

```python
async def connect(self):           # async method
    await self.accept()            # await async call
    
async def receive(self, text_data):
    data = json.loads(text_data)   # sync
    await self.send(...)           # await async call
```

---

## 📚 Next Steps

1. ✅ **Run the demos** - Get familiar with functionality
2. ✅ **Read code comments** - All files are heavily commented
3. ✅ **Modify demos** - Try adding features
4. ✅ **Create new consumer** - Build your own feature
5. ✅ **Deploy** - Put it online (see README.md for details)

---

## 🆘 Need Help?

1. Check README.md for detailed documentation
2. Review inline code comments in consumers.py
3. See troubleshooting section in README.md
4. Check [Django Channels Docs](https://channels.readthedocs.io/)

---

**Happy Coding! 🎉**

*For detailed documentation, see README.md*
