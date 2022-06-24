import logging
import sys

from django.test import TestCase

from questions.models import QuestionCategory
from users.models import MyUser
from ..models import Post

if len(sys.argv) > 1 and sys.argv[1] == 'test':
    logging.disable(logging.CRITICAL)


class TestPostModel(TestCase):
    """Test class for the Post model"""

    @classmethod
    def setUpTestData(cls):
        MyUser.objects.create(first_name='Quentin', last_name='Tarantino', username='QweenTeen',
                              email='queenteen@mail.ru', is_active=True)
        QuestionCategory.objects.create(name='TestCategory')
        author = MyUser.objects.first()
        category = QuestionCategory.objects.first()
        Post.objects.create(title='TestPost', author=author, category=category, body='some text')

    def test_title_max_length(self):
        post = Post.objects.first()
        max_length = post._meta.get_field('title').max_length
        self.assertEquals(max_length, 150)

    def test_string_output_of_the_post_model(self):
        """Post model string output text test"""
        post = Post.objects.first()
        expected_string_output = f'{post.title}'
        self.assertEquals(expected_string_output, str(post))

    def test_new_post_is_not_available_by_default(self):
        post = Post.objects.first()
        self.assertFalse(post.available)
