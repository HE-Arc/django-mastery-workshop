from django.urls import path
from .consumers import BlogConsumer

websocket_urlpatterns = [
    path("ws/blog/", BlogConsumer.as_asgi()),
]
