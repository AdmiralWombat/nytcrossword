from django import template
register = template.Library()

@register.filter
def get(value, i):
    return value[i]