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
        # await executes code and waits for it to finish
        await self.send({
            "type": "websocket.accept"
        })
        # kwargs = username comes from routing.py 
        other_user = self.scope['url_route']['kwargs']['username']
        me = self.scope['user']
        # print(other_user, me)
        # await for async to finish so we get correct object 
        thread_obj = await self.get_thread(me, other_user)
        # print(thread_obj)
        # await asyncio.sleep(10)
    
    async def websocket_receive(self, event): 
        # When a message is received from websocket 
        print("receive", event)
        # {'type': 'websocket.receive', 'text': '{"message":"another!"}'}
        # When you run diff messages and events, type is mapped to wesocket recieve 
        front_text = event.get('text', None)
        if front_text is not None: 
            loaded_dict_data = json.loads(front_text)
            msg = loaded_dict_data.get('message')
            print(msg)

            user = self.scope['user']
            username = 'default'
            if user.is_authenticated: 
                username = user.username
            myResponse = {
                'message': "this is a instant message",
                'username': username 
            }
            await self.send({
                "type": "websocket.send",
                "text": json.dumps(myResponse) # Dictionary to be sent to our front end
            })

    async def websocket_disconnect(self, event): 
        # when socket disconnects 
        print("disconnected", event)
        

    ## Websockets and channels: 
     # Websocket and page can connect and disconnect at the same time        
     # Allows reconnection without page reload 
     # So allows us to handle a whole lot of stuff

    @database_sync_to_async
    def get_thread(self, user, other_username):
        return Thread.objects.get_or_new(user, other_username)[0]