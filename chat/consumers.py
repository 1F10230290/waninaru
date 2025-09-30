import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from .models import Room, Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']

        # 部屋が存在するかチェック
        self.room = await sync_to_async(Room.objects.get)(name=self.room_name)

        # ログインユーザーが参加者か確認
        user = self.scope["user"]
        if user not in [self.room.creator, self.room.craftsman]:
            await self.close()
            return

        self.room_group_name = f'chat_{self.room_name}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # 過去メッセージを送信
        messages = await sync_to_async(list)(self.room.messages.order_by('timestamp'))
        for msg in messages:
            await self.send(text_data=json.dumps({
                'username': msg.sender.profile.name,
                'message': msg.content
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        user = self.scope["user"]

        # DB に保存
        msg_obj = await sync_to_async(Message.objects.create)(
            room=self.room,
            sender=user,
            content=message
        )

        # ルーム全員に送信
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': msg_obj.content,
                'username': user.profile.name
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'username': event['username'],
            'message': event['message']
        }))
