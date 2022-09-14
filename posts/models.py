"""
Stores the post model, which is necessary to provide additional functionality
of the site - small articles for better disclosure of the topic of questions.
"""
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
    """Generates and returns the path for the saved image of the post.
    It is necessary for the orderly storage of images.

    Args:

        * instance (`Post`): an instance of a post being created or modified.
        * filename (`str`): the name under which the post's image will be stored.

    Returns:

        * str: the path to the saved file.
    """
    title_str = instance.title.replace(' ', '_')
    return f'post_images/{title_str}_{filename}'


class Post(models.Model):
    """The model for the post."""
    title = models.CharField(max_length=150)
    author = models.ForeignKey(MyUser, to_field='username', default='drf',  on_delete=models.CASCADE)
    category = models.ForeignKey(QuestionCategory, on_delete=models.CASCADE)
    body = models.TextField()
    image = models.ImageField(blank=True, upload_to=post_image_path)
    created_on = models.DateTimeField(auto_now_add=True)
    available = models.BooleanField(default=False)
    tag = models.CharField(max_length=250, default='IT', db_index=True)

    def __str__(self):
        """Forms a printable representation of the object.
        Returns a post's title.
        """
        return self.title

    def save(self, **kwargs):
        """
        Saves the object. If a post is being created or edited
        and a image is added for it, the selected image will be reduced
        to a certain size of 300x300 (if it is initially larger) and
        will be saved along the generated path.

        The following path to the image will be assigned:
            post_images/{title of post}_{name of the source image file}

        Example:
            * title of post - *A little about generators*
            * name of the source image file - *my_image_file.jpg*
            * path - **post_images/A little about generators_my_image_file.jpg**

        Note:
            it is assumed that the images will have a horizontal orientation,
            the vertical orientation images will be processed incorrectly and should not be used.
        """
        super().save()
        if self.image:
            img = Image.open(self.image.path)

            if img.height > 600 or img.width > 600:
                output_size = (600, 600)
                img.thumbnail(output_size)
                img.save(self.image.path)

    def delete(self, using=None, keep_parents=False):
        """When deleting a post, it also deletes the image belonging to it, if it existed."""
        if self.image:
            self.image.delete(save=False)
        super().delete()

    @property
    def image_url(self):
        """If there is an image for this post and a path to it, it returns this path."""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url


@receiver(pre_save, sender=Post)
def new_post_info(sender, instance, **kwargs):
    """
    Sends an email to the admin if the site user has suggested their own post.

    Posts are initially inactive when they are created. The admin, having received the message,
    can go to the admin panel and consider the proposed post.
    With a positive decision, the post can be activated, and it will replenish the collection of the site.

    Args:

        * sender (`Post`): an instance of a post that a site user creates.
        * instance (`Post`): an instance of a post that a site user creates.

    Note:
        When creating a new post by the admin, an email notification is not sent to him.
    """
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
