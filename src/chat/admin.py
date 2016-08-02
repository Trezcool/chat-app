from django.contrib import admin

from chat.models import ChatGroup, ChatMessage, FriendRequest, Friend, Membership

admin.site.register(FriendRequest)
admin.site.register(Friend)
admin.site.register(ChatGroup)
admin.site.register(Membership)
admin.site.register(ChatMessage)
