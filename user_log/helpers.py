"""Helpers to provide interaction with the user statistics objects."""
import logging
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist

from kafka_files.producer import UserLogProducer

from user_log.models import UserLog


logger = logging.getLogger(__name__)


def create_user_logging(user):
    """Create user statistics object."""
    user_log = UserLog(user=user)
    user_log.save()
    return user_log


def auth_update_user_logging(user):
    """Update user statistics last login."""
    user_log = UserLog.objects.get_or_create(user=user)[0]
    user_log.last_login = datetime.now()
    user_log.save()


def send_statistics_message(user, guessed):
    """
    Send statistics messages to kafka publisher.

    Args:
        user(MyUser): current user.
        guessed (bool): flag, determines if the current question guessed.

    Returns:
        None:
    """
    try:
        user_log = UserLog.objects.get(user=user)
        message = {
            'user_id': user_log.id,
            'guessed': guessed,
        }
        statistics_producer = UserLogProducer()
        statistics_producer.send_msg(msg=message)
    except ObjectDoesNotExist:
        logger.error(
            'User log for user with id %s does not exist.',
            user.id
        )
