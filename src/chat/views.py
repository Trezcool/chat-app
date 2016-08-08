from itertools import chain
from operator import attrgetter

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.transaction import atomic
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic

from chat.models import ChatGroup, ChatMessage, Friend, FriendRequest, Membership


class GroupAdminRequiredMixin(UserPassesTestMixin):
    """
    Requires that the user be the group admin.
    """
    permission_denied_message = 'You do not have admin right to this group.'

    def test_func(self):
        self.raise_exception = True
        label = self.kwargs.get(self.slug_url_kwarg)
        group = get_object_or_404(ChatGroup, label=label)
        return self.request.user == group.admin


class HomeView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'chat/home.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('chats')
        return super().get(request, *args, **kwargs)


class ChatListView(LoginRequiredMixin, generic.ListView):
    model = ChatMessage
    template_name = 'chat/chats.html'

    def get_queryset(self):
        user = self.request.user
        friend_to = user.friend_to.all().values_list('friend', flat=True)
        groups = (ChatGroup.objects.filter(Q(admin=user) | Q(members__in=friend_to))
                                   .distinct().values_list('id', flat=True))
        chat_messages = ChatMessage.objects.filter(Q(sender=user) | Q(receiver=user) | Q(group_id__in=groups))
        friends = user.friends.all().values_list('friend', flat=True)
        latest_messages = ChatMessage.objects.none()
        for friend in friends:
            try:
                latest_message = list([(chat_messages.filter(Q(sender_id=friend, group__isnull=True) |
                                                             Q(receiver_id=friend, group__isnull=True))
                                                     .latest('created'))])
                latest_messages = list(chain(latest_messages, latest_message))
            except ChatMessage.DoesNotExist:
                pass
        for group in groups:
            try:
                latest_message = list([chat_messages.filter(group_id=group).latest('created')])
                latest_messages = list(chain(latest_messages, latest_message))
            except ChatMessage.DoesNotExist:
                pass
        latest_messages = reversed(sorted(latest_messages, key=attrgetter('created')))
        return latest_messages


class P2pChatView(LoginRequiredMixin, generic.DetailView):
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
        if not user.friends.is_friend(receiver):
            raise Http404('You have no relationship with this user.')
        return receiver

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        p2p_list = [self.request.user.pk, self.object.pk]
        msg_count = int(self.request.GET.get('msg_count', 0)) + 10  # Load more messages
        chat_messages = ChatMessage.objects.filter(sender_id__in=p2p_list, receiver_id__in=p2p_list).order_by('-created')
        max_count = chat_messages.count()
        chat_messages = reversed(chat_messages[:msg_count])
        context.update({
            'msg_count': msg_count,
            'max_count': max_count,
            'chat_messages': chat_messages,
        })
        return context


class GroupChatView(LoginRequiredMixin, generic.DetailView):
    model = ChatGroup
    context_object_name = 'group'
    template_name = 'chat/group_chat.html'

    def get_object(self, queryset=None):
        user = self.request.user
        label = self.kwargs.get(self.slug_url_kwarg)
        group = get_object_or_404(ChatGroup, label=label)
        # Check that the session's user is either the admin or a member of this group.
        if user != group.admin:
            if not Membership.objects.is_member(group, user):
                raise Http404('You do not belong to this group.')
        return group

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if getattr(self, 'is_chat', True):
            msg_count = int(self.request.GET.get('msg_count', 0)) + 10  # Load more messages
            chat_messages = self.object.messages.order_by('-created')
            max_count = chat_messages.count()
            chat_messages = reversed(chat_messages[:msg_count])
            context.update({
                'msg_count': msg_count,
                'max_count': max_count,
                'chat_messages': chat_messages,
            })
        return context


class ContactListView(LoginRequiredMixin, generic.ListView):
    model = Friend
    template_name = 'chat/contacts.html'

    def get_queryset(self):
        return self.request.user.friends.all().select_related('friend')


class FavoriteListView(ContactListView):
    template_name = 'chat/favorites.html'

    def get_queryset(self):
        return self.request.user.friends.favorites().select_related('friend')


class GroupListView(LoginRequiredMixin, generic.ListView):
    model = ChatGroup
    template_name = 'chat/groups.html'

    def get_queryset(self):
        user = self.request.user
        friend_to = user.friend_to.all().values_list('friend', flat=True)
        return ChatGroup.objects.filter(Q(admin=user) | Q(members__in=friend_to)).distinct()


class GroupCreateView(LoginRequiredMixin, generic.CreateView):
    model = ChatGroup
    fields = ['name', 'label']
    template_name = 'chat/create_group.html'
    success_url = reverse_lazy('groups')

    def form_valid(self, form):
        form.instance = form.save(commit=False)
        form.instance.admin = self.request.user
        return super().form_valid(form)


class GroupUpdateView(GroupAdminRequiredMixin, GroupChatView, generic.UpdateView):
    fields = ['name', 'label']
    template_name = 'chat/update_group.html'
    success_url = reverse_lazy('groups')
    is_chat = False


class GroupDeleteView(GroupAdminRequiredMixin, GroupChatView, generic.DeleteView):
    template_name = 'chat/group_confirm_delete.html'
    success_url = reverse_lazy('groups')
    is_chat = False


class GroupMemberListView(GroupChatView):
    template_name = 'chat/group_members.html'
    is_chat = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        members_ids = list(self.object.members.all().values_list('id', flat=True))
        members_ids.append(self.object.admin_id)
        members = User.objects.filter(pk__in=members_ids)
        user_friends_ids = self.request.user.friends.all().values_list('friend', flat=True)
        common_friends_ids = list(self.object.members.filter(pk__in=user_friends_ids).values_list('id', flat=True))
        if self.object.admin_id in user_friends_ids:
            common_friends_ids.append(self.object.admin_id)
        context.update({
            'members': members,
            'common_friends_ids': common_friends_ids,
        })
        return context


class GroupMembersAddView(GroupUpdateView):
    fields = ['members']
    template_name = 'chat/add_group_members.html'
    is_chat = False

    def get_form(self, form_class=None):
        """
        Only include the user's friends and exclude those who are already members of the group.
        """
        form = super().get_form(form_class=form_class)
        friends_ids = self.request.user.friends.all().values_list('friend', flat=True)
        members_ids = self.object.members.all().values_list('id', flat=True)
        form.fields['members'].queryset = User.objects.filter(pk__in=friends_ids).exclude(pk__in=members_ids)
        return form

    def form_valid(self, form):
        group = form.save(commit=False)
        for member in form.cleaned_data.get('members'):
            Membership.objects.get_or_create(group=group, member=member)
        group.save()
        return redirect('group_members', group.label)


class PotentialFriendListView(LoginRequiredMixin, generic.ListView):
    model = User
    template_name = 'chat/find_friends.html'

    def get_queryset(self):
        user = self.request.user
        friends = list(user.friends.all().values_list('friend', flat=True))
        friends.append(user.pk)
        return User.objects.exclude(pk__in=friends)


class FriendRequestListView(LoginRequiredMixin, generic.ListView):
    model = FriendRequest
    template_name = 'chat/friend_requests.html'

    def get_queryset(self):
        return self.request.user.receiver_requests.unapproved().select_related('sender')


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
    if potential_friend == user or user.friends.is_friend(potential_friend):
        raise Http404('User already exists in your friend list.')
    FriendRequest.objects.create(sender=user, receiver=potential_friend)
    redirect_to = request.GET['redirect_to']
    redirect_pk = request.GET.get('pk')
    return redirect(redirect_to, redirect_pk) if redirect_pk else redirect(redirect_to)


@login_required
def undo_friend_request(request, pk):
    """
    Cancels a friend request made to a potential friend.
    """
    potential_friend = get_object_or_404(User, pk=pk)
    user = request.user
    if potential_friend == user or user.friends.is_friend(potential_friend):
        raise Http404('User already exists in your friend list.')
    try:
        FriendRequest.objects.get(sender=user, receiver=potential_friend).delete()
    except FriendRequest.DoesNotExist:
        pass  # TODO: Raise ??
    redirect_to = request.GET['redirect_to']
    redirect_pk = request.GET.get('pk')
    return redirect(redirect_to, redirect_pk) if redirect_pk else redirect(redirect_to)


@login_required
def accept_friend_request(request, pk):
    """
    Accepts a friend request made by a potential friend.
    """
    friend_req = get_object_or_404(FriendRequest, pk=pk)
    sender = friend_req.sender
    user = request.user
    if sender == user or user.friends.is_friend(sender):
        raise Http404('User already exists in your friend list.')
    with atomic():
        friend_req.is_approved = True
        friend_req.save()
        # Add each user to the other's friend list.
        Friend.objects.create(owner=user, friend=sender)
        Friend.objects.create(owner=sender, friend=user)
    return redirect('friend_requests')


@login_required
def unfriend_friend(request, pk):
    """
    Unfriends a friend (Deletes both `Friend` instances from each user's friend list).
    """
    user = request.user
    friend = get_object_or_404(Friend, pk=pk)
    if friend.owner != user:
        raise Http404('You have no relationship with this user.')
    user_friend = Friend.objects.get(owner=friend.friend, friend=user)
    friend.delete()
    user_friend.delete()
    return redirect('contacts')


@login_required
def remove_group_member(request, slug, pk):
    """
    Removes a member from a group.
    """
    group = get_object_or_404(ChatGroup, label=slug)
    if request.user != group.admin:
        raise Http404('You do not have admin right to this group.')
    membership = get_object_or_404(Membership, group=group, member_id=pk)
    membership.delete()
    return redirect('group_members', group.label)


@login_required
def leave_group(request, slug):
    """
    Leaves a group.
    """
    user = request.user
    group = get_object_or_404(ChatGroup, label=slug)
    if user == group.admin:
        try:
            next_admin = Membership.objects.filter(group=group).exclude(member=user).earliest('created').member
            group.admin = next_admin
            group.save()
        except Membership.DoesNotExist:  # There's no members but the admin, therefore delete group.
            group.delete()
            return redirect('groups')
    elif not Membership.objects.is_member(group, user):  # Check that user is a member of this group.
        raise Http404('You do not belong to this group.')
    try:
        Membership.objects.get(group=group, member=user).delete()
    except Membership.DoesNotExist:  # user was original admin & not a member.
        pass
    return redirect('groups')


home = HomeView.as_view()
chat_list = ChatListView.as_view()
p2p_chat = P2pChatView.as_view()
group_chat = GroupChatView.as_view()
contact_list = ContactListView.as_view()
favorite_list = FavoriteListView.as_view()
group_list = GroupListView.as_view()
group_create = GroupCreateView.as_view()
group_update = GroupUpdateView.as_view()
group_delete = GroupDeleteView.as_view()
group_member_list = GroupMemberListView.as_view()
group_members_add = GroupMembersAddView.as_view()
potential_friend_list = PotentialFriendListView.as_view()
friend_request_list = FriendRequestListView.as_view()
