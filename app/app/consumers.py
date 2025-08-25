import json
from channels.generic.websocket import AsyncWebsocketConsumer

class YourConsumer(AsyncWebsocketConsumer):
    group_name = "broadcast"

    async def connect(self):
        # join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # leave group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # broadcast incoming message to everyone in group
        try:
            data = json.loads(text_data)
            message = data.get("message", "")
        except:
            message = text_data

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message",
                "message": message
            }
        )

    # called when group_send dispatches
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"]
        }))
