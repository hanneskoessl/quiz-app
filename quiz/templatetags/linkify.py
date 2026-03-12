from django import template
from django.template.defaultfilters import urlize
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def urlize_blank(value):
    result = urlize(value)
    result = result.replace('<a ', '<a target="_blank" rel="noopener noreferrer" ')
    return mark_safe(result)