from users.models import MyUser
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        MyUser.objects.create_superuser('drf', 'd@mail.ru', '1')
