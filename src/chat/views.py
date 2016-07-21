from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import render, get_object_or_404

from chat.models import Room, Message


def chat_room(request, label=None, pk=None):
    """
    Show the chat page, with latest messages.
    The template for this view has the WebSocket business to send and stream
    messages, so see the template for where the magic happens.
    """
    room = receiver = messages = None
    if label:
        room = get_object_or_404(Room, label=label)
        messages = reversed(room.messages.order_by('-created')[:50])
    elif pk:
        sender_pk = request.user.pk
        if pk == str(sender_pk):
            raise Http404
        receiver = get_object_or_404(User, pk=pk)
        p2p_list = [sender_pk, receiver.pk]
        messages = reversed(Message.objects.filter(sender_id__in=p2p_list,
                                                   receiver_id__in=p2p_list).order_by('-created')[:50])

    return render(request, 'base.html', {
        'room': room,
        'receiver': receiver,
        'messages': messages,
    })
