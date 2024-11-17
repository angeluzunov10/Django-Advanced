# pip install markdown

import markdown
from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter(name="markdown")
def markdown_format(text):
    return markdown.markdown(text)