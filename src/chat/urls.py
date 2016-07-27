from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^p2p/(?P<pk>[\w-]{,50})/$', views.chat, name='p2p_chat'),
    url(r'^group/(?P<label>[\w-]{,50})/$', views.chat, name='group_chat'),
]
