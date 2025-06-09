# customers/templatetags/app_filters.py

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Allows accessing dictionary items by key in Django templates.
    Useful for looking up verbose choices from model.CHOICES.
    Example: {{ my_object.MY_CHOICES|get_item:my_object.my_field }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    # Handle Django's choices tuples (e.g., TRIP_STATUS_CHOICES)
    # They are lists of (value, verbose_name) tuples
    if isinstance(dictionary, (list, tuple)):
        for value, verbose_name in dictionary:
            if value == key:
                return verbose_name
    return None # Return None if key not found or not a dict/list of tuples

@register.filter(name='add_class')
def add_class(value, arg):
    """
    Adds a CSS class to a form field's widget.
    Usage: {{ field|add_class:"my-class" }}
    """
    return value.as_widget(attrs={'class': arg})