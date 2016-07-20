from channels.routing import route_class

from chat.consumers import ChatConsumer

channel_routing = [
    route_class(ChatConsumer),
]
