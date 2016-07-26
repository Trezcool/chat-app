from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from chat.models import Room, Message, Contact


class ContactCreateForm(forms.ModelForm):
    def clean_contact(self):
        contact = self.cleaned_data.get('contact')
        if contact == self.cleaned_data.get('owner'):
            raise forms.ValidationError(_('The contact must be different from the owner.'))
        return contact

    class Meta:
        model = Contact
        fields = '__all__'


class RoomCreateForm(forms.ModelForm):
    def clean_contacts(self):
        contacts = self.cleaned_data.get('contacts')
        for contact in contacts:
            if contact.owner != self.cleaned_data.get('owner'):
                raise forms.ValidationError(_("Only this owner's contacts are allowed."))
        return contacts

    class Meta:
        model = Room
        fields = '__all__'


class MessageCreateForm(forms.ModelForm):
    def clean_receiver(self):
        receiver = self.cleaned_data.get('receiver')
        if receiver.owner != self.cleaned_data.get('sender'):
            raise forms.ValidationError(_("Only this owner's contacts are allowed."))
        return receiver

    class Meta:
        model = Message
        fields = '__all__'


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    form = ContactCreateForm


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    form = RoomCreateForm

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == 'contacts':
            try:
                obj_id = request.resolver_match.args[0]
                room = Room.objects.get(pk=obj_id)
                kwargs['queryset'] = Contact.objects.filter(owner=room.owner)
            except IndexError:
                pass
        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    form = MessageCreateForm
