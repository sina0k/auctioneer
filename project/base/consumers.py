import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer


# class AuctionConsumer(WebsocketConsumer):
#     async def connect(self):
#         print("here")
#         self.auction_id = self.scope['url_route']['kwargs']['auctionId']
#         self.room_group_name = 'auction_%s' % self.auction_id

#         # Join room group
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )

#         await self.accept()

#     async def disconnect(self, close_code):
#         # Leave room group
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     async def receive(self, text_data):
#         pass

#     async def new_bid(self, event):
#         message = event['message']

#         await self.send(text_data=message)

class AuctionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.auction_id = self.scope['url_route']['kwargs']['auctionId']
        self.auction_group_name = 'auction_%s' % self.auction_id
        self.channel_layer = get_channel_layer()

        await self.channel_layer.group_add(
            self.auction_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.auction_group_name,
            self.channel_name
        )

    async def new_bid(self, event):
        data = event['data']

        await self.send(text_data=json.dumps(data))
