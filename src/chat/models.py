from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel


class FriendRequest(TimeStampedModel):  # TODO: Create 2 `Friend` instances upon approval.
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sender_requests')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='receiver_requests')
    is_approved = models.BooleanField(default=False)

    class Manager(models.Manager):
        def unapproved(self):
            return self.filter(is_approved=False)

        def is_pending(self, receiver):
            return self.unapproved().filter(receiver=receiver).exists()

    objects = Manager()

    def __str__(self):
        return '{} to {}'.format(self.sender, self.receiver)


class Friend(TimeStampedModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friends')  # owner's friend list.
    friend = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friend_to')
    is_favorite = models.BooleanField(default=False)

    class Manager(models.Manager):
        def is_friend(self, friend):
            return self.filter(friend=friend).exists()

        def favorites(self):  # TODO: via a known `owner`.
            return self.filter(is_favorite=True)

    objects = Manager()

    def __str__(self):
        return '{} (owner: {})'.format(self.friend, self.owner)


class ChatGroup(TimeStampedModel):
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='chat_groups')
    name = models.CharField(max_length=15)
    label = models.SlugField(unique=True)
    is_public = models.BooleanField(default=False)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Membership', blank=True)  # TODO: owner's friends

    def __str__(self):
        return self.label


class Membership(TimeStampedModel):
    group = models.ForeignKey(ChatGroup)
    member = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Manager(models.Manager):
        def is_member(self, group, user):
            friend_ids = user.friend_to.all().values_list('friend', flat=True)
            return self.filter(group=group, member__in=friend_ids).exists()

    objects = Manager()

    def __str__(self):
        return '{} member of {}'.format(self.member, self.group)


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
        return self.created.strftime('%-I:%M %p')

    @property
    def timestamp_date(self):
        return self.created.date()

    def as_dict(self):
        return {
            'sender': self.sender.username,
            'message': self.message,
            'timestamp': self.formatted_timestamp
        }
