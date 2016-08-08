from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from chat.forms import AdminUserChangeForm, AdminCreationForm
from chat.models import ChatGroup, ChatMessage, FriendRequest, Friend, Membership, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    readonly_fields = ('last_login', 'date_joined')
    form = AdminUserChangeForm
    add_form = AdminCreationForm


admin.site.register(FriendRequest)
admin.site.register(Friend)
admin.site.register(ChatGroup)
admin.site.register(Membership)
admin.site.register(ChatMessage)
