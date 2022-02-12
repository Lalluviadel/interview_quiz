from datetime import timedelta

from PIL import Image
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now


def users_image_path(instance, filename):
    return f'user_images/{instance.username}_{filename}'


class MyUser(AbstractUser):
    img = models.ImageField(blank=True, upload_to=users_image_path)
    email = models.EmailField(unique=True)
    score = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=False)
    activation_key = models.CharField(max_length=128, blank=True, null=True)
    activation_key_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f'{self.first_name} "{self.username}"'

    def save(self, **kwargs):
        super().save()
        if self.img:
            img = Image.open(self.img.path)

            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.img.path)

    def is_activation_key_expired(self):
        """The activation key is issued for 48 hours"""
        if now() <= self.activation_key_created + timedelta(hours=48):
            return False
        return True
