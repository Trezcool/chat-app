from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView

from chat import views
from chat.api import urls as api_urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(api_urls)),
    url(r'^p2p/(?P<pk>[\w-]{,50})/$', views.chat_room, name='p2p_chat'),
    url(r'^group/(?P<label>[\w-]{,50})/$', views.chat_room, name='group_chat'),
    url(r'^.*$', TemplateView.as_view(template_name='base.html'), name='ngapp'),
]
