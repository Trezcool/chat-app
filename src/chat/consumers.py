import logging
from django.contrib.auth.models import User
from channels.generic.websockets import JsonWebsocketConsumer

from chat.models import ChatGroup, ChatMessage, Membership

log = logging.getLogger(__name__)


class ChatConsumer(JsonWebsocketConsumer):
    http_user = True
    group = None
    receiver = None

    def __init__(self, message, **kwargs):
        """
        Performs some validations before initiating the connexion.
        """
        try:
            # Expected path formats: `/chat/p2p/:id/` or `/chat/group/:label/`
            prefix, chat_type, label = message['path'].strip('/').split('/')
            if prefix != 'chats' or chat_type not in ['p2p', 'group']:
                log.debug('invalid ws path=%s', message['path'])
                return
            if chat_type == 'p2p':  # Peer-to-peer chat: check that a receiver with this ID exists.
                try:
                    self.receiver = User.objects.get(pk=label)
                except User.DoesNotExist:
                    log.debug('ws receiver does not exist id=%s', label)
                    return
            elif chat_type == 'group':  # Group chat: check that a group with this label exists.
                try:
                    self.group = ChatGroup.objects.get(label=label)
                except ChatGroup.DoesNotExist:
                    log.debug('ws group does not exist label=%s', label)
                    return
            self.label = label
        except ValueError:
            log.debug('invalid ws path=%s', message['path'])
            return
        super().__init__(message, **kwargs)

    def connection_groups(self, **kwargs):
        """
        Returns the group name based on the chat type.
        """
        if self.receiver:  # Peer-to-peer chat
            p2p_label = '-'.join(sorted(map(str, [self.message.user.pk, self.label])))
            return ['p2p-{}'.format(p2p_label)]
        return ['group-{}'.format(self.label)]

    def raw_connect(self, message, **kwargs):
        """
        Checks that the session's user is a friend to the receiver if it's a p2p chat or
        checks that he is a member of this group if it's a group chat.
        """
        user = message.user
        if not user.is_authenticated():
            return
        if self.receiver:  # Peer-to-peer chat
            if user.pk == self.receiver.pk:
                log.debug("ws receiver (id=%s) is the same as sender", self.label)
                return
            if not user.friends.is_friend(self.receiver):
                log.debug("ws sender (id=%s) is not a friend to receiver (id=%s)", user.pk, self.label)
                return
        else:  # Group chat
            if user != self.group.admin:
                if not Membership.objects.is_member(self.group, user):
                    log.debug("ws sender (id=%s) do not belong to group (label=%s)", user.pk, self.label)
                    return
        super().raw_connect(message, **kwargs)

    def receive(self, content, **kwargs):
        """
        Saves the message in the DB and echo it back to all group's channels.
        """
        if set(content.keys()) != {'message'}:
            log.debug("ws message unexpected format data=%s", content)
            return
        if content:
            content.update({'sender': self.message.user})
            if self.group:  # Group chat
                message = self.group.messages.create(**content)
            else:  # Peer-to-peer chat
                content.update({'receiver': self.receiver})
                message = ChatMessage.objects.create(**content)
            self.group_send(self.connection_groups()[0], message.as_dict())
