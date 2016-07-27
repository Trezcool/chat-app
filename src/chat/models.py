from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel


class FriendRequest(TimeStampedModel):  # TODO: Create 2 `Friend` instances upon approval.
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sender_requests')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='receiver_requests')
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return '{} to {}'.format(self.sender.__str__(), self.receiver.__str__())


class Friend(TimeStampedModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friends')
    friend = models.ForeignKey(settings.AUTH_USER_MODEL)

    def __str__(self):
        return '{} (owner: {})'.format(self.friend.__str__(), self.owner.__str__())


class ChatGroup(TimeStampedModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='chat_groups')
    name = models.CharField(max_length=15)
    label = models.SlugField(unique=True)
    is_public = models.BooleanField(default=False)
    friends = models.ManyToManyField(Friend, related_name='chat_groups', blank=True)  # TODO: owner's friends

    def __str__(self):
        return self.label


class ChatMessage(TimeStampedModel):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sender_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='receiver_messages', blank=True, null=True)  # TODO: sender's friend
    group = models.ForeignKey(ChatGroup, related_name='messages', blank=True, null=True)
    message = models.TextField()

    def __str__(self):
        if self.receiver:
            return '[{timestamp}] {sender} to {receiver}: {message}'.format(receiver=self.receiver, **self.as_dict())
        return '[{timestamp}] {sender} to {group}: {message}'.format(group=self.group, **self.as_dict())

    @property
    def formatted_timestamp(self):
        return self.created.strftime('%b %-d %-I:%M %p')

    def as_dict(self):
        return {
            'sender': self.sender.username,
            'message': self.message,
            'timestamp': self.formatted_timestamp
        }
