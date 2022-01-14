from PIL import Image
from django.db import models

from questions.models import QuestionCategory
from users.models import MyUser


def post_image_path(instance, filename):
    title_str = instance.title.replace(' ', '_')
    return f'post_images/{title_str}_{filename}'


class Post(models.Model):
    title = models.CharField(max_length=150)
    author = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    category = models.ForeignKey(QuestionCategory, on_delete=models.CASCADE)
    body = models.TextField()
    image = models.ImageField(blank=True, upload_to=post_image_path)
    created_on = models.DateTimeField(auto_now_add=True)
    available = models.BooleanField(default=False)
    tag = models.CharField(max_length=250, default='IT', db_index=True)

    def __str__(self):
        return self.title

    def save(self, **kwargs):
        super().save()
        if self.image:
            img = Image.open(self.image.path)

            if img.height > 600 or img.width > 600:
                output_size = (600, 600)
                img.thumbnail(output_size)
                img.save(self.image.path)

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
