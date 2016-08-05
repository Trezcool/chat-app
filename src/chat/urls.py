from django.conf.urls import url
from django.contrib import admin

from chat import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.home, name='home'),

    # Chats
    url(r'^chats/$', views.chat_list, name='chats'),
    url(r'^chats/p2p/(?P<pk>[\w-]{,50})/$', views.p2p_chat, name='p2p_chat'),
    url(r'^chats/group/(?P<slug>[\w-]{,50})/$', views.group_chat, name='group_chat'),

    # Contacts
    url(r'^contacts/$', views.contact_list, name='contacts'),
    url(r'^contacts/(?P<pk>[\w-]{,50})/unfriend/$', views.unfriend_friend, name='unfriend'),

    # Favorites
    url(r'^favorites/$', views.favorite_list, name='fav'),
    url(r'^favorites/(?P<pk>[\w-]{,50})/$', views.toggle_favorite, name='toggle_fav'),

    # Groups.
    url(r'^groups/$', views.group_list, name='groups'),
    url(r'^groups/create/$', views.group_create, name='create_group'),
    url(r'^groups/(?P<slug>[\w-]{,50})/update/$', views.group_update, name='update_group'),
    url(r'^groups/(?P<slug>[\w-]{,50})/delete/$', views.group_delete, name='delete_group'),
    url(r'^groups/(?P<slug>[\w-]{,50})/members/$', views.group_member_list, name='group_members'),
    url(r'^groups/(?P<slug>[\w-]{,50})/leave/$', views.leave_group, name='leave_group'),

    # Friend requests.
    url(r'^friend-requests/$', views.friend_request_list, name='friend_requests'),
    url(r'^friend-requests/(?P<pk>[\w-]{,50})/send/$', views.send_friend_request, name='send_request'),
    url(r'^friend-requests/(?P<pk>[\w-]{,50})/undo/$', views.undo_friend_request, name='undo_request'),
    url(r'^friend-requests/(?P<pk>[\w-]{,50})/accept/$', views.accept_friend_request, name='accept_request'),

    url(r'^potential-friends/$', views.potential_friend_list, name='potential_friends'),
]
