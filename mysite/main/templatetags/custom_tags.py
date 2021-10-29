from django import template
from django.template import Library, Node, TemplateSyntaxError
from uuid import uuid4

register = template.Library()

def cut(value, arg):
    """Removes all values of arg from the given string"""
    return value.replace(arg, '')


@register.simple_tag
def createuuid(var):
    return str(uuid4())