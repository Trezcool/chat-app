from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel


class Contact(TimeStampedModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='contacts')
    contact = models.ForeignKey(settings.AUTH_USER_MODEL)  # TODO: owner's contact

    def __str__(self):
        return '{} (owner: {})'.format(self.contact.__str__(), self.owner.__str__())


class Room(TimeStampedModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    name = models.CharField(max_length=15)
    label = models.SlugField(unique=True)
    is_public = models.BooleanField(default=False)
    contacts = models.ManyToManyField(Contact, related_name='rooms', blank=True)  # TODO: owner's contacts

    def __str__(self):
        return self.label


class Message(TimeStampedModel):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='messages')
    receiver = models.ForeignKey(Contact, related_name='messages', blank=True, null=True)  # TODO: sender's contact
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
