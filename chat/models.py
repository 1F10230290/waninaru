from django.db import models
from django.conf import settings

class Room(models.Model):
    """
    個別チャットルーム
    room_name は "creatorid_craftsmanid" の形式でユニーク
    """
    name = models.CharField(max_length=255, unique=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='creator_rooms', on_delete=models.CASCADE
    )
    craftsman = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='craftsman_rooms', on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.creator.email} ⇄ {self.craftsman.email}"

class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.email}: {self.content[:20]}"

