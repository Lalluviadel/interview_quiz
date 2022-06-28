"""
Stores the user model that is necessary for the interaction of site visitors with its content.
"""
from datetime import timedelta
from uuid import uuid4

from PIL import Image
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now


def users_image_path(instance, filename):
    """Generates and returns the path for the saved avatar of the user.
    It is necessary for the orderly storage of images.

    Args:

        * instance (`MyUser`): an instance of a user being created or modified.
        * filename (`str`): the name under which the user's image will be stored.

    Returns:

        * str: the path to the saved file.
    """
    return f'user_images/{instance.username}_{filename}'


class MyUser(AbstractUser):
    """The model for the user."""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    img = models.ImageField(blank=True, upload_to=users_image_path)
    email = models.EmailField(unique=True)
    score = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=False, db_index=True)
    activation_key = models.CharField(max_length=128, blank=True, null=True)
    activation_key_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    info = models.BooleanField(default=True)

    def __str__(self):
        """Forms a printable representation of the object.
        Returns user's firstname and username.
        """
        return f'{self.first_name} "{self.username}"'

    def save(self, **kwargs):
        """
        Saves the object. If a user edits his profile and wants to set
        an avatar or change it, the selected image is reduced to a size
        of 300x300 (if it is initially larger) and saved along the generated path.

        The following path to the image will be assigned:
            user_images/{username of the profile owner}_{name of the source image file}

        Example:
            * username of the profile owner - *Test_user*
            * name of the source image file - *my_image_file.jpg*
            * path - **user_images/Test_user_my_image_file.jpg**

        Note:
            it is assumed that the images will have a horizontal orientation,
            the vertical orientation images will be processed incorrectly and should not be used.
        """
        if 'update_fields' in kwargs:
            super().save(update_fields=kwargs['update_fields'])
            if self.img and 'img' in kwargs['update_fields']:
                img = Image.open(self.img.path)

                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.img.path)
        else:
            super().save()

    def delete(self, using=None, keep_parents=False):
        """When deleting a user, it also deletes the image belonging to it, if it existed."""
        if self.img:
            self.img.delete(save=False)
        super().delete()

    def is_activation_key_expired(self):
        """If the user has not managed to activate his profile during this time,
        he will have to register again.
        """
        if now() <= self.activation_key_created + timedelta(hours=48):
            return False
        return True
