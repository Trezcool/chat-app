from django.conf.urls import url

from chat import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^chats/$', views.chat_list, name='chats'),
    url(r'^p2p/(?P<pk>[\w-]{,50})/$', views.chat_session, name='p2p_chat'),
    url(r'^group/(?P<label>[\w-]{,50})/$', views.chat_session, name='group_chat'),
]
