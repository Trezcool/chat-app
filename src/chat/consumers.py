import logging
from django.contrib.auth.models import User
from channels.generic.websockets import JsonWebsocketConsumer

from chat.models import Room, Message


log = logging.getLogger(__name__)


class ChatConsumer(JsonWebsocketConsumer):
    http_user = True

    def __init__(self, message, **kwargs):
        try:
            prefix, chat_type, label = message['path'].strip('/').split('/')
            if prefix != 'chat' or chat_type not in ['p2p', 'group']:
                log.debug('invalid ws path=%s', message['path'])
                return
            if chat_type == 'p2p' and not User.objects.filter(pk=label).exists():
                log.debug('receiver does not exist id=%s', label)
                return
            if chat_type == 'group' and not Room.objects.filter(label=label).exists():
                log.debug('ws room does not exist label=%s', label)
                return
            self.chat_type = chat_type
            self.label = label
        except ValueError:
            log.debug('invalid ws path=%s', message['path'])
            return
        super().__init__(message, **kwargs)

    @staticmethod
    def get_p2p_label(pk1, pk2):
        sorted_pk_list = sorted(map(str, [pk1, pk2]))
        return '-'.join(sorted_pk_list)

    def connection_groups(self, **kwargs):
        if self.chat_type == 'p2p':  # person-to-person chat
            p2p_label = 'p2p-{}'.format(self.get_p2p_label(self.message.user.pk, self.label))
            return [p2p_label]
        return ['group-{}'.format(self.label)]

    def connect(self, message, **kwargs):
        self.message.channel_session['sender'] = message.user.pk
        self.message.channel_session['group_name'] = self.connection_groups()[0]
        if self.chat_type == 'p2p':  # person-to-person chat
            self.message.channel_session['receiver'] = self.label
            return
        self.message.channel_session['room'] = self.label

    def receive(self, content, **kwargs):
        room = label = receiver = None
        session = self.message.channel_session
        try:
            label = session['room']
            room = Room.objects.get(label=label)
        except KeyError:  # Not a group chat
            try:
                label = session['receiver']
                receiver = User.objects.get(pk=label)
            except User.DoesNotExist:
                log.debug('received message, user does not exist id=%s', label)
                return
        except Room.DoesNotExist:
            log.debug('received message, room does not exist label=%s', label)
            return
        if set(content.keys()) != {'message'}:
            log.debug("ws message unexpected format data=%s", content)
            return
        if content:
            try:
                sender = User.objects.get(pk=session['sender'])
            except User.DoesNotExist:
                return
            content.update({'sender': sender})
            if room:  # Group chat
                # log.debug('chat message room=%s handle=%s message=%s', room.label, data['handle'], data['message'])
                m = room.messages.create(**content)
            else:  # person-to-person chat
                content.update({'receiver': receiver})
                # log.debug('chat message room=%s handle=%s message=%s', room.label, data['handle'], data['message'])
                m = Message.objects.create(**content)
            self.group_send(session['group_name'], m.as_dict())
