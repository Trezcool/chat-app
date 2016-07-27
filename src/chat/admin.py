from django.contrib import admin

from chat.models import ChatGroup, ChatMessage, FriendRequest, Friend

admin.site.register(FriendRequest)
admin.site.register(Friend)
admin.site.register(ChatGroup)
admin.site.register(ChatMessage)
