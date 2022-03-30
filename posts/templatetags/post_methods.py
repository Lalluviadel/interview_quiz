from django import template

register = template.Library()


@register.filter(name='filter_set')
def filter_set(queryset):
    filtered_set = queryset.filter(available=True)
    return filtered_set
