"""Helpers to provide interaction with the user statistics objects."""
from datetime import datetime

from user_log.models import UserLog


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
