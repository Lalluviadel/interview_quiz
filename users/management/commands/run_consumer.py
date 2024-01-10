"""Contains custom command for easy run consumer by manage.py."""
from django.core.management import BaseCommand

from interview_quiz.settings import KAFKA_ENABLED

from kafka_files.consumer import UserLogConsumer


class Command(BaseCommand):
    """Django command class."""

    def handle(self, *args, **options):
        """Run and test user statistics consumer."""
        if KAFKA_ENABLED:
            consumer = UserLogConsumer()
            for message in consumer.consumer:
                consumer.get_message(message)
