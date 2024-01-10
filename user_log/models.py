"""
User statistics collection models.
"""
from django.db import models

from users.models import MyUser


class UserLog(models.Model):
    """The model for the user statistics collection."""

    question_count = models.PositiveIntegerField(default=0)
    right_answers = models.PositiveIntegerField(default=0)
    wrong_answers = models.PositiveIntegerField(default=0)
    last_login = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(
        MyUser, to_field='username',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        """
        Forms a printable representation of the object.

        Returns the name of the category.
        """
        return f'{self.user.username} statistics'
