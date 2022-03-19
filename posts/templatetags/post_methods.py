from django import template

register = template.Library()


@register.filter(name='filter_set')
def filter_set(queryset):
    filtered_set = queryset.filter(available=True)
    return filtered_set


@register.filter(name='count_posts')
def count_posts(queryset):
    return filter_set(queryset).count()
