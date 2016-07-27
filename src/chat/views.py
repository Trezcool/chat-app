from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import render, get_object_or_404

from chat.models import ChatGroup, ChatMessage, Friend


def chat(request, label=None, pk=None):
    """
    Show the chat page, with latest messages.
    The template for this view has the WebSocket business to send and stream
    messages, so see the template for where the magic happens.
    """
    group = receiver = messages = None
    user = request.user
    if user.is_authenticated():
        if label:
            group = get_object_or_404(ChatGroup, label=label)
            # Check that the session's user is a member of this group.
            is_member = False
            if user.pk == group.owner_id:
                is_member = True
            else:
                friend_ids = Friend.objects.filter(friend=user).values_list('id', flat=True)
                group_friend_ids = group.friends.all().values_list('id', flat=True)
                for friend_id in friend_ids:
                    if friend_id in group_friend_ids:
                        is_member = True
                        break
            if not is_member:
                raise Http404('You do not belong to this group.')
            messages = reversed(group.messages.order_by('-created')[:50])
        elif pk:
            if pk == str(user.pk):
                raise Http404('You cannot message yourself.')
            receiver = get_object_or_404(User, pk=pk)
            # Check that the `receiver` is a friend to the session's user.
            if not Friend.objects.filter(owner=user, friend=receiver).exists():
                raise Http404('You have no relationship with this user.')
            p2p_list = [user.pk, receiver.pk]
            messages = reversed(ChatMessage.objects.filter(sender_id__in=p2p_list,
                                                           receiver_id__in=p2p_list).order_by('-created')[:50])

    return render(request, 'base.html', {
        'room': group,
        'receiver': receiver,
        'messages': messages,
    })
