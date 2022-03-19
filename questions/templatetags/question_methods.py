from django import template

from interview_quiz.variabls import CHOICE_NAME

register = template.Library()


@register.filter(name='choice_name')
def choice_name(item):
    name = CHOICE_NAME[item]
    return name
