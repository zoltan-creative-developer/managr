from django import template
register = template.Library()

@register.filter
def key(d, k):
    return d.get(k)