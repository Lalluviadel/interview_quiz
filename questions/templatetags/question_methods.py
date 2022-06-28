"""Stores custom template tags related to the operation of the question model."""
from django import template

from interview_quiz.variabls import CHOICE_NAME

register = template.Library()


@register.filter(name='choice_name')
def choice_name(item):
    """Replaces the difficulty level values with those adapted to the question model."""
    name = CHOICE_NAME[item]
    return name
