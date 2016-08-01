from itertools import chain
from operator import attrgetter

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.transaction import atomic
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views import generic

from chat.models import ChatGroup, ChatMessage, Friend, FriendRequest


class HomeView(generic.TemplateView, LoginRequiredMixin):
    template_name = 'chat/home.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect('chats')
        return super().get(request, *args, **kwargs)


class ChatListView(generic.ListView, LoginRequiredMixin):
    model = ChatMessage
    template_name = 'chat/chats.html'

    def get_queryset(self):
        user = self.request.user
        friend_to = Friend.objects.filter(friend=user).values_list('id', flat=True)
        groups = (ChatGroup.objects.filter(Q(owner=user) | Q(friends__in=friend_to))
                                   .distinct().values_list('id', flat=True))
        chat_messages = ChatMessage.objects.filter(Q(sender=user) | Q(receiver=user) | Q(group_id__in=groups))
        friends = user.friends.all().values_list('friend_id', flat=True)
        latest_messages = ChatMessage.objects.none()
        try:
            for friend in friends:
                latest_message = list([(chat_messages.filter(Q(sender_id=friend, group__isnull=True) |
                                                             Q(receiver_id=friend, group__isnull=True))
                                                     .latest('created'))])
                latest_messages = list(chain(latest_messages, latest_message))
            for group in groups:
                latest_message = list([chat_messages.filter(group_id=group).latest('created')])
                latest_messages = list(chain(latest_messages, latest_message))
        except ChatMessage.DoesNotExist:
            pass
        latest_messages = reversed(sorted(latest_messages, key=attrgetter('created')))
        return latest_messages


class P2pChatView(generic.DetailView, LoginRequiredMixin):
    model = User
    context_object_name = 'receiver'
    template_name = 'chat/p2p_chat.html'

    def get_object(self, queryset=None):
        user = self.request.user
        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk == str(user.pk):
            raise Http404('You cannot message yourself.')
        receiver = get_object_or_404(User, pk=pk)
        # Check that the `receiver` is a friend to the session's user.
        if not Friend.objects.is_friend(owner=user, friend=receiver):
            raise Http404('You have no relationship with this user.')
        return receiver

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        p2p_list = [self.request.user.pk, self.object.pk]
        msg_count = kwargs.get('msg_count', 0) + 10  # TODO: Implement `Loading of more messages`
        chat_messages = reversed(ChatMessage.objects.filter(sender_id__in=p2p_list,
                                                            receiver_id__in=p2p_list).order_by('-created')[:msg_count])
        context.update({
            'msg_count': msg_count,
            'chat_messages': chat_messages,
        })
        return context


class GroupChatView(generic.DetailView, LoginRequiredMixin):
    model = ChatGroup
    context_object_name = 'group'
    template_name = 'chat/group_chat.html'

    def get_object(self, queryset=None):
        user = self.request.user
        label = self.kwargs.get(self.slug_url_kwarg)
        group = get_object_or_404(ChatGroup, label=label)
        # Check that the session's user is either the owner or a member of this group.
        if not user.pk == group.owner_id:
            if not ChatGroup.objects.is_member(group_id=group.pk, user=user):
                raise Http404('You do not belong to this group.')
        return group

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        msg_count = kwargs.get('msg_count', 0) + 10  # TODO: Implement `Loading of more messages`
        chat_messages = reversed(self.object.messages.order_by('-created')[:msg_count])
        context.update({
            'msg_count': msg_count,
            'chat_messages': chat_messages,
        })
        return context


class ContactListView(generic.ListView, LoginRequiredMixin):
    model = Friend
    template_name = 'chat/contacts.html'

    def get_queryset(self):
        return self.request.user.friends.all().select_related('friend')


class FavoriteListView(ContactListView):
    template_name = 'chat/favorites.html'

    def get_queryset(self):
        return self.request.user.friends.favorites().select_related('friend')


class GroupListView(generic.ListView, LoginRequiredMixin):
    model = ChatGroup
    template_name = 'chat/groups.html'

    def get_queryset(self):
        user = self.request.user
        friend_to = Friend.objects.filter(friend=user).values_list('id', flat=True)
        return ChatGroup.objects.filter(Q(owner=user) | Q(friends__in=friend_to)).distinct()


class PotentialFriendListView(generic.ListView, LoginRequiredMixin):
    model = User
    template_name = 'chat/find_friends.html'

    def get_queryset(self):
        user = self.request.user
        friends = user.friends.all().values_list('friend_id', flat=True)
        return User.objects.exclude(Q(pk=user.pk) | Q(friends__in=friends))


class FriendRequestListView(generic.ListView, LoginRequiredMixin):
    model = FriendRequest
    template_name = 'chat/friend_requests.html'

    def get_queryset(self):
        return self.request.user.receiver_requests.unapproved()


@login_required
def toggle_favorite(request, pk):
    """
    Toggles the friend's `is_favorite` field.
    """
    friend = get_object_or_404(Friend, pk=pk)
    if friend.owner != request.user:
        raise Http404('You have no relationship with this user.')
    friend.is_favorite = not friend.is_favorite
    friend.save()
    return redirect(request.GET['redirect_to'])


@login_required
def send_friend_request(request, pk):
    """
    Sends a friend request to a potential friend.
    """
    potential_friend = get_object_or_404(User, pk=pk)
    user = request.user
    if potential_friend == user or user.friends.filter(friend=potential_friend).exists():
        raise Http404('User already exists in your friend list.')
    FriendRequest.objects.create(sender=user, receiver=potential_friend)
    return redirect('potential_friends')


@login_required
def undo_friend_request(request, pk):
    """
    Cancels a friend request made to a potential friend.
    """
    potential_friend = get_object_or_404(User, pk=pk)
    user = request.user
    if potential_friend == user or user.friends.filter(friend=potential_friend).exists():
        raise Http404('User already exists in your friend list.')
    try:
        FriendRequest.objects.get(sender=user, receiver=potential_friend).delete()
    except FriendRequest.DoesNotExist:
        pass  # TODO: Raise ??
    return redirect('potential_friends')


@login_required
def accept_friend_request(request, pk):
    """
    Accepts a friend request made by a potential friend.
    """
    friend_req = get_object_or_404(FriendRequest, pk=pk)
    sender = friend_req.sender
    user = request.user
    if sender == user or user.friends.filter(friend=sender).exists():
        raise Http404('User already exists in your friend list.')
    with atomic():
        friend_req.is_approved = True
        friend_req.save()
        # Add each user to the other's friend list.
        Friend.objects.create(owner=user, friend=sender)
        Friend.objects.create(owner=sender, friend=user)
    return redirect('friend_requests')


home = HomeView.as_view()
chat_list = ChatListView.as_view()
p2p_chat = P2pChatView.as_view()
group_chat = GroupChatView.as_view()
contact_list = ContactListView.as_view()
favorite_list = FavoriteListView.as_view()
group_list = GroupListView.as_view()
potential_friend_list = PotentialFriendListView.as_view()
friend_request_list = FriendRequestListView.as_view()
