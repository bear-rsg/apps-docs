import re
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter()
def dot_wbr(value):
    return mark_safe(".<wbr>".join(value.split('.')))


@register.filter()
def to_a_name(value):
    not_allowed_characters = re.compile('[^a-zA-Z0-9]')
    return re.sub(not_allowed_characters, '', value).lower()


@register.simple_tag
def website_settings_value(name):
    if name in settings.WEBSITE_SITE_CONFIG:
        return settings.WEBSITE_SITE_CONFIG[name]
    else:
        return "UNDEFINED"
