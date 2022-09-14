"""Contains custom commands for easy launch by manage.py."""
from users.models import MyUser
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    """A command for quickly creating a superuser."""
    def handle(self, *args, **options):
        user = MyUser.objects.create_superuser('qwerty', 'd@mail.ru', '1')
        user.is_active = True
        user.save()
