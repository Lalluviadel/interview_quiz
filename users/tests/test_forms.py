import logging
import sys

from django.test import SimpleTestCase, TestCase

from ..forms import UserLoginForm, UserRegisterForm, UserProfileForm, UserImgChangeProfileForm, WriteAdminForm, \
    MyPasswordResetForm
from ..models import MyUser

if len(sys.argv) > 1 and sys.argv[1] == 'test':
    logging.disable(logging.CRITICAL)


class TestUserLoginForm(SimpleTestCase):

    def test_login_form_fields_placeholders(self):
        form = UserLoginForm()
        self.assertTrue(form.fields['username'].widget.attrs['placeholder'] == 'Введите имя пользователя')
        self.assertTrue(form.fields['password'].widget.attrs['placeholder'] == 'Введите пароль')


class TestUserRegisterForm(TestCase):

    def __init__(self, *args, **kwargs):
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
        form = UserRegisterForm()
        self.assertTrue(form.fields['username'].widget.attrs['placeholder'] == 'Введите имя пользователя')
        self.assertTrue(form.fields['email'].widget.attrs['placeholder'] == 'Введите адрес эл.почты')
        self.assertTrue(form.fields['first_name'].widget.attrs['placeholder'] == 'Введите имя')
        self.assertTrue(form.fields['last_name'].widget.attrs['placeholder'] == 'Введите фамилию')
        self.assertTrue(form.fields['password1'].widget.attrs['placeholder'] == 'Введите пароль')
        self.assertTrue(form.fields['password2'].widget.attrs['placeholder'] == 'Подтвердите пароль')

    def test_too_short_username(self):
        form_data = self.form_data
        form_data['username'] = 'Qt'
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_num_username(self):
        form_data = self.form_data
        form_data['username'] = '123'
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_too_short_first_name(self):
        form_data = self.form_data
        form_data['first_name'] = 'Que'
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_num_first_name(self):
        form_data = self.form_data
        form_data['first_name'] = '123'
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_too_short_last_name(self):
        form_data = self.form_data
        form_data['last_name'] = 'Tar'
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_num_last_name(self):
        form_data = self.form_data
        form_data['last_name'] = '123'
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_valid_activation_key_being_created(self):
        form_data = self.form_data
        form = UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())
        form.save()
        user = MyUser.objects.get(username=form_data['username'])
        self.assertTrue(user.activation_key)

    def test_one_user_created(self):
        """Form health test and verification of the creation of a new record"""
        data = self.form_data
        data['email'] = 'new_unique_email@example.ru'
        form = UserRegisterForm(data=self.form_data)
        form.is_valid()
        form.save()
        assert MyUser.objects.filter(email=self.form_data['email']).count() == 1


class TestUserProfileForm(SimpleTestCase):

    def test_user_profile_form_fields_readonly(self):
        form = UserProfileForm()
        self.assertTrue(form.fields['username'].widget.attrs['readonly'])
        self.assertTrue(form.fields['email'].widget.attrs['readonly'])

    def test_user_profile_form_img_field_class(self):
        form = UserProfileForm()
        self.assertTrue(form.fields['img'].widget.attrs['class'] == 'custom-file-input')


class TestUserImgChangeProfileForm(SimpleTestCase):

    def test_user_change_profile_form_img_field_id_assigned(self):
        form = UserImgChangeProfileForm()
        self.assertTrue(form.fields['img'].widget.attrs['id'] == 'avatar')


class TestWriteAdminForm(SimpleTestCase):

    def test_write_admin_form_fields_labels(self):
        form = WriteAdminForm()
        self.assertTrue(form.fields['title'].label == 'Заголовок сообщения')
        self.assertTrue(form.fields['content'].label == 'Текст сообщения')
        self.assertTrue(form.fields['grade'].label == 'Поставьте оценку нашему сайту от 1 до 10')

    def test_title_max_length(self):
        form = WriteAdminForm()
        self.assertEquals(form.fields['title'].max_length, 255)

    def test_grade_min_max_value(self):
        form = WriteAdminForm()
        self.assertEquals(form.fields['grade'].min_value, 1)
        self.assertEquals(form.fields['grade'].max_value, 10)


class TestMyPasswordResetForm(SimpleTestCase):

    def test_password_reset_form_email_placeholder(self):
        form = MyPasswordResetForm()
        self.assertTrue(form.fields['email'].widget.attrs['placeholder'] == 'Введите ваш email')

    def test_no_reset_password_for_an_unregistered_email(self):
        form_data = {'email': 'somenotvalidemail@mail.ru'}
        form = MyPasswordResetForm(data=form_data)
        self.assertFalse(form.is_valid())
