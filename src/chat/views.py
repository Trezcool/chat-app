from itertools import chain
from operator import attrgetter

from django.contrib.auth.models import User
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views import generic

from chat.models import ChatGroup, ChatMessage, Friend


class HomeView(generic.TemplateView):
    template_name = 'chat/home.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect('chats')
        return super().get(request, *args, **kwargs)


class ChatListView(generic.TemplateView):
    template_name = 'chat/chats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        friend_to = Friend.objects.filter(friend=user).values_list('id', flat=True)
        groups = ChatGroup.objects.filter(Q(owner=user) | Q(friends__in=friend_to)).distinct().values_list('id', flat=True)
        chat_messages = ChatMessage.objects.filter(Q(sender=user) | Q(receiver=user) | Q(group_id__in=groups))
        friends = Friend.objects.filter(owner=user).values_list('friend_id', flat=True)
        latest_messages = ChatMessage.objects.none()
        try:
            for friend in friends:
                latest_message = list([chat_messages.filter(Q(sender_id=friend, group__isnull=True) |
                                                            Q(receiver_id=friend, group__isnull=True)).latest('created')])
                latest_messages = list(chain(latest_messages, latest_message))
            for group in groups:
                latest_message = list([chat_messages.filter(group_id=group).latest('created')])
                latest_messages = list(chain(latest_messages, latest_message))
        except ChatMessage.DoesNotExist:
            pass
        latest_messages = reversed(sorted(latest_messages, key=attrgetter('created')))
        context['latest_messages'] = latest_messages
        return context


class ChatSessionView(generic.TemplateView):
    template_name = 'chat/chat_session.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = receiver = chat_messages = None
        label = kwargs.get('label')
        pk = kwargs.get('pk')
        user = self.request.user
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
            chat_messages = reversed(group.messages.order_by('-created')[:50])
        elif pk:
            if pk == str(user.pk):
                raise Http404('You cannot message yourself.')
            receiver = get_object_or_404(User, pk=pk)
            # Check that the `receiver` is a friend to the session's user.
            if not Friend.objects.filter(owner=user, friend=receiver).exists():
                raise Http404('You have no relationship with this user.')
            p2p_list = [user.pk, receiver.pk]
            chat_messages = reversed(ChatMessage.objects.filter(sender_id__in=p2p_list,
                                                                receiver_id__in=p2p_list).order_by('-created')[:50])
        context.update({
            'group': group,
            'receiver': receiver,
            'chat_messages': chat_messages,
        })
        return context


home = HomeView.as_view()
chat_list = ChatListView.as_view()
chat_session = ChatSessionView.as_view()
