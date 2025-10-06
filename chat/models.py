from django.db import models
from django.conf import settings

# チャットルーム
class Room(models.Model):
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

# メッセージ内容
class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.email}: {self.content[:20]}"

# スカウト
class ScoutOffer(models.Model):
    craftsman = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='sent_scouts',
        on_delete=models.CASCADE
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='received_scouts',
        on_delete=models.CASCADE
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.craftsman.email} → {self.creator.email}"