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
        # kwargs = username comes from routing.py 
        other_user = self.scope['url_route']['kwargs']['username']
        me = self.scope['user']
        # print(other_user, me)
        # await for async to finish so we get correct object 
        thread_obj = await self.get_thread(me, other_user)
        print(me, thread_obj.id)
        self.thread_obj = thread_obj 

        chat_room = f"thread_{thread_obj.id}"
        self.chat_room = chat_room 
        await self.channel_layer.group_add(
            chat_room, 
            self.channel_name 
        )

        # await executes code and waits for it to finish
        await self.send({
            "type": "websocket.accept"
        })
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
                'message': msg,
                'username': username 
            }

            await self.create_chat_message(user, msg)

            # braodcasts the message event to be sent 
            await self.channel_layer.group_send(
                self.chat_room,
                {
                    "type": "chat_message",
                    "text": json.dumps(myResponse)
                }
            )
            
    # custom method 
    async def chat_message(self, event): 
        #Send the actual message 
        await self.send({
            "type": "websocket.send",
            "text": event['text']
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

    @database_sync_to_async
    def create_chat_message(self,me, msg):
        thread_obj = self.thread_obj 
        return ChatMessage.objects.create(thread=thread_obj, user=me, message=msg)