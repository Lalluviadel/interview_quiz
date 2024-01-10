"""
Category and question models.

Stores category and question models that are necessary for
the main process of the application - user testing.
"""

import logging

from PIL import Image

from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string

from interview_quiz.settings import (
    ADMIN_USERNAME, DOMAIN_NAME, EMAIL_HOST_USER
)

from users.models import MyUser

logger = logging.getLogger(__name__)


def category_image_path(instance, filename):
    """
    Generate the path for the saved images.

    Generates and returns the path for the saved images
    of the category. It is necessary for the orderly storage
    of images.

    Args:
        * instance (`QuestionCategory`): an instance of
            a category being created or modified.
        * filename (`str`): the name under which the image
            to the category will be stored.

    Returns:
        * str: the path to the saved file.
    """
    return f'cat_images/{instance.name}_{filename}'


def question_image_path(instance, filename):
    """
    Generate the path for the saved images.

    Generates and returns the path for the saved images
    of the question. It is necessary for the orderly storage
    of images.

    Args:
        * instance (`Question`): an instance of a question
            being created or modified.
        * filename (`str`): the name under which the image to
            the question will be stored.

    Returns:
        * str: the path to the saved file.
    """
    question_str = instance.question.replace(' ', '_')
    return f'que_images/{instance.subject}/{question_str}_{filename}'


class QuestionCategory(models.Model):
    """The model for the category."""

    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to=category_image_path,
        blank=True,
        default='default_icons/external-link(new).png'
    )
    available = models.BooleanField(default=True, db_index=True)

    def __str__(self):
        """
        Forms a printable representation of the object.

        Returns the name of the category.
        """
        return self.name

    def save(self, **kwargs):
        """
        Save the object.

        Saves the object and if it has images, reduces them
        to a size of 600x300, forms a path to the images and
        saves them.

        The following path to the image will be assigned:
            cat_images/{category name}_{name of the source image file}

        Example:
            * category name - *Python*
            * image file name - *my_image_file.jpg*
            * path - **cat_images/Python_my_image_file.jpg**

        Note:
            it is assumed that the images will have a horizontal orientation,
            the vertical orientation images will be processed
            incorrectly and should not be used.
        """
        super().save()
        if self.image:
            img = Image.open(self.image.path)

            if img.height > 600 or img.width > 600:
                output_size = (600, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)

    @property
    def image_url(self):
        """
        Return image path.

        If there is an image for this category and a path to it,
        it returns this path.
        """
        if self.image and hasattr(self.image, 'url'):
            return self.image.url

    def delete(self, using=None, keep_parents=False):
        """
        Delete category and its image.

        When deleting a category, it also deletes the image
        belonging to it, if it existed.
        """
        if self.image:
            self.image.delete(save=False)
        super().delete()


class Question(models.Model):
    """The model for the category."""

    NEWBIE = 'NB'
    AVERAGE = 'AV'
    SMARTYPANTS = 'SP'

    #: options for the level of difficulty of the question, on which
    # the number of points received / lost depends
    DIFFICULTY_LEVEL_CHOICES = (
        (NEWBIE, 'новичок'),
        (AVERAGE, 'середнячок'),
        (SMARTYPANTS, 'умник'),
    )

    question = models.CharField(max_length=250)
    subject = models.ForeignKey(
        QuestionCategory, on_delete=models.CASCADE,
        default='1'
    )
    author = models.ForeignKey(
        MyUser, to_field='username',
        on_delete=models.CASCADE, default='drf'
    )
    right_answer = models.CharField(max_length=150, default='default')
    answer_01 = models.CharField(max_length=150, default='default')
    answer_02 = models.CharField(max_length=150, default='default')
    answer_03 = models.CharField(max_length=150, default='default')
    answer_04 = models.CharField(max_length=150, default='default')

    difficulty_level = models.CharField(
        choices=DIFFICULTY_LEVEL_CHOICES,
        verbose_name='уровень', max_length=2,
        default=NEWBIE, db_index=True
    )
    available = models.BooleanField(default=False, db_index=True)
    tag = models.CharField(max_length=250, default='IT')

    image_01 = models.ImageField(upload_to=question_image_path, blank=True)
    image_02 = models.ImageField(upload_to=question_image_path, blank=True)
    image_03 = models.ImageField(upload_to=question_image_path, blank=True)

    def __str__(self):
        """
        Forms a printable representation of the object.

        Returns the content of the question.
        """
        return self.question

    def save(self, **kwargs):
        """
        Save the object.

        Saves the object and if it has images, reduces them
        to a size of 600x600, forms a path to the images and
        saves them.

        The following path to the image will be assigned:
            que_images/{category name}/{question content}_{
            name of the source image file}

        Example:
            * category name - *Python*
            * question content - *"What is a list?"*
            * image file name - *my_image_file.jpg*
            * path - **que_images/Python/What_is_a_list_my_image_file.jpg**

        Note:
            it is assumed that the images will have a horizontal
            orientation, the vertical orientation images will be
            processed incorrectly and should not be used.
        """
        super().save()
        for image in (self.image_01, self.image_02, self.image_03):
            try:
                img = Image.open(image.path)
                if img.height > 600 or img.width > 600:
                    output_size = (600, 600)
                    img.thumbnail(output_size)
                    img.save(image.path)
            except ValueError as e:
                logger.error('Ошибка обработки фото для нового вопроса %s', e)

    def delete(self, using=None, keep_parents=False):
        """
        Delete question and its images.

        When deleting a question, it also deletes the images
        belonging to it, if it existed.
        """
        for image in (self.image_01, self.image_02, self.image_03):
            try:
                if image:
                    image.delete(save=False)
            except ValueError as e:
                logger.debug(
                    'Попытка удаления несуществующего файла изображения %s', e
                )
        super().delete()


@receiver(pre_save, sender=Question)
def new_question_info(sender, instance, **kwargs):
    """
    Send an email about new question to the admin.

    Sends an email to the admin if the site user has suggested
    their own question. Questions are initially inactive when
    they are created. The admin, having received the message,
    can go to the admin panel and consider the proposed question.
    With a positive decision, the question can be activated, and it
    will replenish the collection of the site.

    Args:
        * sender (`Question`): an instance of a question that
            a site user creates.
        * instance (`Question`): an instance of a question that
            a site user creates.

    Note:
        When creating a new question by the admin, an email
        notification is not sent to him.
    """
    if not instance.pk and instance.author.username not in ADMIN_USERNAME:
        subject = 'Предложен новый вопрос'
        context = {
            'user': instance.author.username,
            'my_site_name': DOMAIN_NAME,
            'subject': instance.subject,
        }
        message = render_to_string('emails/new_question.html', context)
        send_mail(subject, message, EMAIL_HOST_USER, [EMAIL_HOST_USER],
                  html_message=message, fail_silently=False)
