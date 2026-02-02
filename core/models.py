from django.db import models
from django.conf import settings

# Create your models here.
class Chat(models.Model):
    room_name = models.CharField(max_length=255)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    # users = models.ManyToManyField('auth.User', related_name='chats')

    def __str__(self):
        return f"[{self.timestamp}] {self.room_name}: {self.message[:20]}..."
    


class ChatMessage(models.Model):
    room_name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='chat_messages',
        null=True,
        blank=True
    )
    user_name = models.CharField(max_length=100)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"[{self.timestamp}] {self.user_name} in {self.room_name}: {self.message[:20]}..."