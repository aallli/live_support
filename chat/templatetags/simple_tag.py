from django import template
from chat.models import *

register = template.Library()


@register.simple_tag()
def is_online_support_operator(request):
    operator = Operator.objects.filter(name=request.user.username).first()
    return operator is not None


@register.simple_tag()
def on_call(request):
    operator = Operator.objects.filter(name=request.user.username).first()
    return operator.status != 'off'