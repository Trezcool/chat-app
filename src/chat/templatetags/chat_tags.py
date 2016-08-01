from django.template import Library

register = Library()


@register.simple_tag(takes_context=True)
def is_request_pending(context, potential_friend):
    user = context['request'].user
    return user.sender_requests.is_pending(potential_friend)
