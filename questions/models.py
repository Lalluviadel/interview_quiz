from PIL import Image
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string

from interview_quiz.settings import ADMIN_USERNAME, DOMAIN_NAME, EMAIL_HOST_USER
from users.models import MyUser


def question_image_path(instance, filename):
    question_str = instance.question.replace(' ', '_')
    return f'que_images/{instance.subject}/{question_str}_{filename}'


def category_image_path(instance, filename):
    return f'cat_images/{instance.name}_{filename}'


class QuestionCategory(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to=category_image_path, blank=True)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        super().save()
        if self.image:
            img = Image.open(self.image.path)

            if img.height > 600 or img.width > 600:
                output_size = (600, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url


class Question(models.Model):
    NEWBIE = 'NB'
    AVERAGE = 'AV'
    SMARTYPANTS = 'SP'

    DIFFICULTY_LEVEL_CHOICES = (
        (NEWBIE, 'новичок'),
        (AVERAGE, 'середнячок'),
        (SMARTYPANTS, 'умник'),
    )

    question = models.CharField(max_length=250)
    subject = models.ForeignKey(QuestionCategory, on_delete=models.CASCADE, default='1')
    author = models.ForeignKey(MyUser, to_field='username', on_delete=models.CASCADE, default='drf')
    right_answer = models.CharField(max_length=150, default='default')
    answer_01 = models.CharField(max_length=150, default='default')
    answer_02 = models.CharField(max_length=150, default='default')
    answer_03 = models.CharField(max_length=150, default='default')
    answer_04 = models.CharField(max_length=150, default='default')

    difficulty_level = models.CharField(choices=DIFFICULTY_LEVEL_CHOICES, verbose_name='уровень', max_length=2,
                                        default=NEWBIE)
    available = models.BooleanField(default=False)
    tag = models.CharField(max_length=250, default='IT')

    image_01 = models.ImageField(upload_to=question_image_path, blank=True)
    image_02 = models.ImageField(upload_to=question_image_path, blank=True)
    image_03 = models.ImageField(upload_to=question_image_path, blank=True)

    def __str__(self):
        return self.question

    def save(self, **kwargs):
        super().save()
        for i in (self.image_01, self.image_02, self.image_03):
            try:
                img = Image.open(i.path)
                if img.height > 600 or img.width > 600:
                    output_size = (600, 600)
                    img.thumbnail(output_size)
                    img.save(i.path)
            except ValueError:
                pass


@receiver(pre_save, sender=Question)
def new_question_info(sender, instance, **kwargs):
    if not instance.pk and instance.author.username not in ADMIN_USERNAME:
        subject = f"Предложен новый вопрос"
        context = {
            'user': instance.author.username,
            'my_site_name': DOMAIN_NAME,
            'subject': instance.subject,
        }
        message = render_to_string('emails/new_question.html', context)
        send_mail(subject, message, EMAIL_HOST_USER, [EMAIL_HOST_USER],
                  html_message=message, fail_silently=False)
