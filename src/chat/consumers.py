import json
import logging

from django.contrib.auth.models import User

from channels import Group
from channels.auth import http_session_user
from channels.sessions import channel_session

from chat.models import Room, Message


log = logging.getLogger(__name__)


def get_p2p_label(pk1, pk2):
    sorted_pk_list = sorted(map(str, [pk1, pk2]))
    return '-'.join(sorted_pk_list)


@channel_session
@http_session_user
def ws_connect(message):
    try:
        prefix, chat_type, label = message['path'].strip('/').split('/')
        if prefix != 'chat':
            log.debug('invalid ws path=%s', message['path'])
            return
        message.channel_session['sender'] = message.user.pk
        if chat_type == 'p2p':  # person-to-person chat
            p2p_label = 'p2p-{}'.format(get_p2p_label(message.user.pk, label))
            Group(p2p_label, channel_layer=message.channel_layer).add(message.reply_channel)
            message.channel_session['receiver'] = label
            message.channel_session['p2p_label'] = p2p_label
            return
        room = Room.objects.get(label=label)
    except ValueError:
        log.debug('invalid ws path=%s', message['path'])
        return
    except Room.DoesNotExist:
        log.debug('ws room does not exist label=%s', label)
        return
    log.debug('chat connect room=%s client=%s:%s', room.label, message['client'][0], message['client'][1])
    Group('group-'+label, channel_layer=message.channel_layer).add(message.reply_channel)
    message.channel_session['room'] = label


@channel_session
def ws_receive(message):
    room = label = receiver = None
    session = message.channel_session
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
    # Parse out a chat message from the content text, bailing if it doesn't
    # conform to the expected message format.
    try:
        data = json.loads(message['text'])
    except ValueError:
        log.debug("ws message not in json format")
        return
    if set(data.keys()) != {'message'}:
        log.debug("ws message unexpected format data=%s", data)
        return
    if data:
        try:
            sender = User.objects.get(pk=session['sender'])
        except User.DoesNotExist:
            return
        data.update({'sender': sender})
        if room:  # Group chat
            # log.debug('chat message room=%s handle=%s message=%s', room.label, data['handle'], data['message'])
            m = room.messages.create(**data)
            Group('group-'+label, channel_layer=message.channel_layer).send({'text': json.dumps(m.as_dict())})
        else:  # person-to-person chat
            data.update({'receiver': receiver})
            # log.debug('chat message room=%s handle=%s message=%s', room.label, data['handle'], data['message'])
            m = Message.objects.create(**data)
            Group(session['p2p_label'], channel_layer=message.channel_layer).send({'text': json.dumps(m.as_dict())})


@channel_session
def ws_disconnect(message):
    try:
        label = message.channel_session['room']
        Room.objects.get(label=label)
        Group('group-'+label, channel_layer=message.channel_layer).discard(message.reply_channel)
    except (KeyError, Room.DoesNotExist):
        pass
