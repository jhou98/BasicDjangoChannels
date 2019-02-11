"""
Consumer is like how views.py is to django, just to channels 

"""
import asyncio
import json
from django.contrib.auth import get_user_model 
from channels.consumer import AsyncConsumer 
from channels.db import database_sync_to_async

from .models import Thread, ChatMessage

class ChatConsumer(AsyncConsumer): 
    async def websocket_connect(self, event): 
        print("connected", event)
    
    async def websocket_receive(self, event): 
        # When a message is received from websocket 
        print("receive", event)

    async def websocket_dicconnect(self, event): 
        # when socket disconnects 
        print("disconnected", event)

    ## Websockets and channels: 
     # Websocket and page can connect and disconnect at the same time          # Allows reconnection without page reload 
     # So allows us to handle a whole lot of stuff