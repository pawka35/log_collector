from django import forms, template
from django.forms import Field


register = template.Library()


@register.filter
def add_class(field: Field, css: str) -> str:
    """Add a class to a field."""
    return field.as_widget(attrs={'class': css})
