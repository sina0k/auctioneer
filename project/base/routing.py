from django.urls import path

from .consumers import AuctionConsumer

websocket_urlpatterns = [
    path("ws/auction/<str:auctionId>", AuctionConsumer.as_asgi(), name="auction_ws"),
]