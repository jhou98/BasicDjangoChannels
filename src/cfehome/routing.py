from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url 
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator 

from chat.consumers import ChatConsumer 
application = ProtocolTypeRouter({
    # Empty for now (http->django views added by default)
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            # To be able to access users 
            URLRouter(
                [
                   url(r"^messages/(?P<username>[\w.@+-]+)/$", ChatConsumer),
                ]
            )
        )
    )
})

# ws://ourdomain/<username> 