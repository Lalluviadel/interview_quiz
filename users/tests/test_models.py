"""
Contains unit and integration tests for checking the models of the web application.
"""
import logging
import sys
from datetime import timedelta

from django.test import TestCase

from ..models import MyUser

if len(sys.argv) > 1 and sys.argv[1] == 'test':
    logging.disable(logging.CRITICAL)


class TestUserModel(TestCase):
    """Test class for the MyUser model."""

    @classmethod
    def setUpTestData(cls):
        """Set up non-modified MyUser object used by all test methods."""
        MyUser.objects.create(first_name='Quentin', last_name='Tarantino', email='queenteen@mail.ru')

    def test_first_name_label(self):
        """MyUser model first name field Label test."""
        user = MyUser.objects.first()
        field_label = user._meta.get_field('first_name').verbose_name
        self.assertEquals(field_label, 'имя')

    def test_last_name_label(self):
        """MyUser model last name field Label test."""
        user = MyUser.objects.first()
        field_label = user._meta.get_field('last_name').verbose_name
        self.assertEquals(field_label, 'фамилия')

    def test_username_label(self):
        """MyUser model username field Label test."""
        user = MyUser.objects.first()
        field_label = user._meta.get_field('username').verbose_name
        self.assertEquals(field_label, 'имя пользователя')

    def test_first_name_max_length(self):
        """MyUser model first name field max length test."""
        user = MyUser.objects.first()
        max_length = user._meta.get_field('first_name').max_length
        self.assertEquals(max_length, 150)

    def test_last_name_max_length(self):
        """MyUser model last name field max length test."""
        user = MyUser.objects.first()
        max_length = user._meta.get_field('last_name').max_length
        self.assertEquals(max_length, 150)

    def test_username_max_length(self):
        """MyUser model username field max length test."""
        user = MyUser.objects.first()
        max_length = user._meta.get_field('username').max_length
        self.assertEquals(max_length, 150)

    def test_string_output_of_the_model(self):
        """MyUser model string output text test."""
        user = MyUser.objects.first()
        expected_string_output = f'{user.first_name} "{user.username}"'
        self.assertEquals(expected_string_output, str(user))

    def test_activation_key_expired_false(self):
        """MyUser model test initial state of the field activation_key_created - not expired."""
        user = MyUser.objects.first()
        self.assertFalse(user.is_activation_key_expired())

    def test_activation_key_expired_true(self):
        """MyUser model test state of the field activation_key_created after 48 hours - expired."""
        user = MyUser.objects.first()
        user.activation_key_created -= timedelta(hours=49)
        user.save(update_fields=['activation_key_created'])
        self.assertTrue(user.is_activation_key_expired())
