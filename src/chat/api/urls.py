from django.conf.urls import url, include

from bo_drf.routers import FlexiRouter
from rest_auth.views import LoginView

router = FlexiRouter()
router.add(r'^login/$', LoginView.as_view(), name='login')


urlpatterns = [
    url(r'^drf/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^', include(router.urls)),
]
