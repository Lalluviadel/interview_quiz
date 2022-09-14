"""
Contains unit and integration tests for checking the forms of the web application.
"""
import logging
import sys

from django.test import SimpleTestCase, TestCase

from ..forms import UserLoginForm, UserRegisterForm, UserProfileForm, UserImgChangeProfileForm, WriteAdminForm, \
    MyPasswordResetForm
from ..models import MyUser

if len(sys.argv) > 1 and sys.argv[1] == 'test':
    logging.disable(logging.CRITICAL)


class TestUserLoginForm(SimpleTestCase):
    """Testing the user authorization form."""

    def test_login_form_fields_placeholders(self):
        """Testing of placeholders filling in the user authorization form fields."""
        form = UserLoginForm()
        self.assertTrue(form.fields['username'].widget.attrs['placeholder'] == 'Введите имя пользователя')
        self.assertTrue(form.fields['password'].widget.attrs['placeholder'] == 'Введите пароль')


class TestUserRegisterForm(TestCase):
    """Testing the new user registration form."""

    def __init__(self, *args, **kwargs):
        """Preparation of data for tests."""
        super().__init__(*args, **kwargs)
        self.form_data = {
            'username': 'PyQT',
            'first_name': 'Quentin',
            'last_name': 'Tarantino',
            'email': 'quieteen@mail.ru',
            'password1': 'QwEnTeEn123',
            'password2': 'QwEnTeEn123',
        }

    def test_register_form_fields_placeholders(self):
        """Testing of placeholders filling in the user registration form fields."""
        form = UserRegisterForm()
        self.assertTrue(form.fields['username'].widget.attrs['placeholder'] == 'Введите имя пользователя')
        self.assertTrue(form.fields['email'].widget.attrs['placeholder'] == 'Введите адрес эл.почты')
        self.assertTrue(form.fields['first_name'].widget.attrs['placeholder'] == 'Введите имя')
        self.assertTrue(form.fields['last_name'].widget.attrs['placeholder'] == 'Введите фамилию')
        self.assertTrue(form.fields['password1'].widget.attrs['placeholder'] == 'Введите пароль')
        self.assertTrue(form.fields['password2'].widget.attrs['placeholder'] == 'Подтвердите пароль')

    def test_too_short_username(self):
        """Testing the lack of validity of the form if the username is too short."""
        form_data = self.form_data
        form_data['username'] = 'Qt'
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_num_username(self):
        """Testing the lack of validity of the form if the username consists only of digits."""
        form_data = self.form_data
        form_data['username'] = '123'
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_too_short_first_name(self):
        """Testing the lack of validity of the form if the firstname is too short."""
        form_data = self.form_data
        form_data['first_name'] = 'Que'
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_num_first_name(self):
        """Testing the lack of validity of the form if the firstname consists only of digits."""
        form_data = self.form_data
        form_data['first_name'] = '123'
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_too_short_last_name(self):
        """Testing the lack of validity of the form if the lasname is too short."""
        form_data = self.form_data
        form_data['last_name'] = 'Tar'
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_num_last_name(self):
        """Testing the lack of validity of the form if the lastname consists only of digits."""
        form_data = self.form_data
        form_data['last_name'] = '123'
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_valid_activation_key_being_created(self):
        """Testing the creation of an activation key during the registration of a new user."""
        form_data = self.form_data
        form = UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())
        form.save()
        user = MyUser.objects.get(username=form_data['username'])
        self.assertTrue(user.activation_key)

    def test_one_user_created(self):
        """Form health test and verification of the creation of a new record."""
        data = self.form_data
        data['email'] = 'new_unique_email@example.ru'
        form = UserRegisterForm(data=self.form_data)
        form.is_valid()
        form.save()
        assert MyUser.objects.filter(email=self.form_data['email']).count() == 1


class TestUserProfileForm(SimpleTestCase):
    """Testing the user profile form."""

    def test_user_profile_form_fields_readonly(self):
        """Testing the read-only fields of the user profile form."""
        form = UserProfileForm()
        self.assertTrue(form.fields['username'].widget.attrs['readonly'])
        self.assertTrue(form.fields['email'].widget.attrs['readonly'])

    def test_user_profile_form_img_field_class(self):
        """Testing the user profile form img field class."""
        form = UserProfileForm()
        self.assertTrue(form.fields['img'].widget.attrs['class'] == 'custom-file-input')


class TestUserImgChangeProfileForm(SimpleTestCase):
    """Testing the user profile editing form."""

    def test_user_change_profile_form_img_field_id_assigned(self):
        """Testing the association of the id of the img field of the user profile editing form."""
        form = UserImgChangeProfileForm()
        self.assertTrue(form.fields['img'].widget.attrs['id'] == 'avatar')


class TestWriteAdminForm(SimpleTestCase):
    """Testing the form of writing a message to the admin."""

    def test_write_admin_form_fields_labels(self):
        """Testing the labels of the fields of the message writing form to the admin."""
        form = WriteAdminForm()
        self.assertTrue(form.fields['title'].label == 'Заголовок сообщения')
        self.assertTrue(form.fields['content'].label == 'Текст сообщения')
        self.assertTrue(form.fields['grade'].label == 'Поставьте оценку нашему сайту от 1 до 10')

    def test_title_max_length(self):
        """Testing the set maximum length of the title field of the message writing form to the admin."""
        form = WriteAdminForm()
        self.assertEquals(form.fields['title'].max_length, 255)

    def test_grade_min_max_value(self):
        """Testing the maximum and minimum values of the grade
        field of the form of writing a message to the administrator."""
        form = WriteAdminForm()
        self.assertEquals(form.fields['grade'].min_value, 1)
        self.assertEquals(form.fields['grade'].max_value, 10)


class TestMyPasswordResetForm(SimpleTestCase):
    """Testing the password recovery form."""

    def test_password_reset_form_email_placeholder(self):
        """Testing the placeholder of the email field of the password recovery form."""
        form = MyPasswordResetForm()
        self.assertTrue(form.fields['email'].widget.attrs['placeholder'] == 'Введите ваш email')

    def test_no_reset_password_for_an_unregistered_email(self):
        """Testing the lack of validation of the password recovery form when specifying
        an email that was not used during registration."""
        form_data = {'email': 'somenotvalidemail@mail.ru'}
        form = MyPasswordResetForm(data=form_data)
        self.assertFalse(form.is_valid())
