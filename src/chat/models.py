from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel


class Room(TimeStampedModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    name = models.CharField(max_length=15)
    label = models.SlugField(unique=True)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.label


class Message(TimeStampedModel):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sender_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='receiver_messages', blank=True, null=True)
    room = models.ForeignKey(Room, related_name='messages', blank=True, null=True)
    message = models.TextField()

    def __str__(self):
        if self.receiver:
            return '[{timestamp}] {sender} to {receiver}: {message}'.format(receiver=self.receiver, **self.as_dict())
        return '[{timestamp}] {sender} to {room}: {message}'.format(room=self.room, **self.as_dict())

    @property
    def formatted_timestamp(self):
        return self.created.strftime('%b %-d %-I:%M %p')

    def as_dict(self):
        return {
            'sender': self.sender.username,
            'message': self.message,
            'timestamp': self.formatted_timestamp
        }
