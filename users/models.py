from PIL import Image
from django.contrib.auth.models import AbstractUser
from django.db import models


def users_image_path(instance, filename):
    return f'user_images/{instance.username}_{filename}'


class MyUser(AbstractUser):
    img = models.ImageField(blank=True, upload_to=users_image_path)
    email = models.EmailField(unique=True)
    score = models.PositiveIntegerField(default=0)

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
