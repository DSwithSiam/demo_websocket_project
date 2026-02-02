"""
ASGI config for demo_websocket_project project.

This file configures the ASGI application for handling both HTTP and WebSocket protocols.
It uses Django Channels to enable real-time WebSocket communication.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
https://channels.readthedocs.io/
"""

import os
import django

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demo_websocket_project.settings')

# Initialize Django to load all apps
django.setup()

# Import WebSocket routing after Django is initialized
from core.routing import websocket_urlpatterns
from core.jwd_middleware import JWTAuthMiddlewareStack

# ============================================================================
# ASGI APPLICATION CONFIGURATION
# ============================================================================
# This is the main entry point for ASGI servers like Daphne, Uvicorn, etc.
# It routes incoming connections based on protocol type:
# - HTTP requests go to Django
# - WebSocket connections go to Django Channels
# ============================================================================

application = ProtocolTypeRouter({
    # HTTP protocol handler - standard Django ASGI application
    'http': get_asgi_application(),
    
    # WebSocket protocol handler - Django Channels with authentication
    'websocket': AllowedHostsOriginValidator(
        JWTAuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        )
    ),
})
