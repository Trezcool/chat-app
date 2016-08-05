from django import forms
from chat.models import ChatGroup, Friend, Membership


class GroupCreateForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(queryset=Friend.objects.none(), required=False)

    class Meta:
        model = ChatGroup
        exclude = ['admin', 'is_public']

    def __init__(self, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(**kwargs)
        self.fields['members'].queryset = Friend.objects.filter(owner=self.user)

    def save(self, commit=False):
        instance = super().save(commit)
        instance.admin = self.user
        instance.save()
        for member in self.cleaned_data.get('members'):
            Membership.objects.create(member=member, group=instance)
        return instance
