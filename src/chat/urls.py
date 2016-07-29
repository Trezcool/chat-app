from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from chat import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.home, name='home'),
    url(r'^chats/$', views.chat_list, name='chats'),
    url(r'^p2p/(?P<pk>[\w-]{,50})/$', views.p2p_chat, name='p2p_chat'),
    url(r'^group/(?P<slug>[\w-]{,50})/$', views.group_chat, name='group_chat'),
    url(r'^contacts/$', views.contact_list, name='contacts'),
    url(r'^fav/$', views.favorite_list, name='fav'),
    url(r'^groups/$', views.group_list, name='groups'),
    url(r'^toggle-fav/(?P<pk>[\w-]{,50})/$', login_required(views.toggle_favorite), name='toggle_fav'),
]
