from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Chat Room APIs
    path('rooms/', views.list_chat_rooms, name='list_rooms'),
    path('rooms/create/', views.create_chat_room, name='create_room'),

    # Chat History APIs
    path('chat/history/<str:room_name>/', views.get_chat_history, name='get_chat_history'),
    path('chat/history/<str:room_name>/delete/', views.delete_chat_history, name='delete_chat_history'),

    # WebSocket Connection Info
    path('ws/info/<str:room_name>/', views.get_websocket_info, name='websocket_info'),
]
