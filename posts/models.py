from PIL import Image
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string

from interview_quiz.settings import ADMIN_USERNAME, DOMAIN_NAME, EMAIL_HOST_USER
from questions.models import QuestionCategory
from users.models import MyUser


def post_image_path(instance, filename):
    title_str = instance.title.replace(' ', '_')
    return f'post_images/{title_str}_{filename}'


class Post(models.Model):
    title = models.CharField(max_length=150)
    author = models.ForeignKey(MyUser, to_field='username', default='drf',  on_delete=models.CASCADE)
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


@receiver(pre_save, sender=Post)
def new_post_info(sender, instance, **kwargs):
    if not instance.pk and instance.author.username not in ADMIN_USERNAME:
        subject = f"Предложена новая статья"
        context = {
            'user': instance.author.username,
            'my_site_name': DOMAIN_NAME,
            'title': instance.title,
            'category': instance.category,
        }
        message = render_to_string('emails/new_post.html', context)
        send_mail(subject, message, EMAIL_HOST_USER, [EMAIL_HOST_USER],
                  html_message=message, fail_silently=False)
