from uuid import uuid4
from django.conf import settings
from django.db import models
from django.db.models import UUIDField

from model_utils.models import TimeStampedModel


class Token(TimeStampedModel):
    key = UUIDField(primary_key=True, default=uuid4)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='auth_token')

    def __str__(self):
        return self.key.hex
