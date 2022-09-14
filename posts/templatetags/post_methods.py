"""Stores custom template tags related to the operation of the post model."""
from django import template

register = template.Library()


@register.filter(name='filter_set')
def filter_set(queryset):
    """Filters the queryset, leaving only active objects. Returns a filtered queryset."""
    filtered_set = queryset.filter(available=True)
    return filtered_set
