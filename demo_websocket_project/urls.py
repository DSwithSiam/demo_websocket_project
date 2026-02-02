"""
URL configuration for demo_websocket_project project.

API-only configuration with Swagger documentation.
"""

from django.contrib import admin
from django.urls import path, include

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Swagger/OpenAPI Schema Configuration
schema_view = get_schema_view(
    openapi.Info(
        title="WebSocket Chat API",
        default_version='v1',
        description="""
        REST API for WebSocket Chat Application

        Features:
        - User Registration & Authentication
        - Chat Room Management
        - Chat History
        - WebSocket Connection Info

        WebSocket Endpoints:
        - ws://host/ws/chat/{room_name}/ - Chat room WebSocket
        - ws://host/ws/notifications/{user_id}/ - User notifications WebSocket
        - ws://host/ws/counter/ - Shared counter WebSocket
        """,
        contact=openapi.Contact(email="admin@chatapp.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Swagger/OpenAPI Documentation
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Admin panel
    path('admin/', admin.site.urls),

    # Accounts app URLs (User registration, login)
    path('api/v1/auth/', include('accounts.urls')),

    # Core chat API URLs
    path('api/v1/chat/', include('core.urls')),
]

