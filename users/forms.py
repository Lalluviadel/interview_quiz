import hashlib
import logging
from random import random

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm, PasswordResetForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from users.models import MyUser

logger = logging.getLogger(__name__)


def len_validation(obj, field, field_name):
    name_len = len(field)
    if name_len <= 3:
        msg = ValidationError(obj.error_messages[f'invalid_{field_name}'],
                              code=f'invalid_{field_name}',
                              params={'value': name_len})
        obj.add_error(f'{field_name}', msg)
    num_validation(obj, field, field_name)
    return field


def num_validation(obj, field, field_name):
    if field.isdigit():
        msg = ValidationError(obj.error_messages['only_digits'],
                              code='only_digits', )
        obj.add_error(f'{field_name}', msg)
    return field


class UserLoginForm(AuthenticationForm):
    error_messages = {
        'invalid_login': _(
            "Пожалуйста, введите верный логин и пароль с учетом регистра"
        ),
    }

    class Meta:
        model = MyUser
        fields = ('username', 'password')

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Введите имя пользователя'
        self.fields['password'].widget.attrs['placeholder'] = 'Введите пароль'
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control py-4'


class UserRegisterForm(UserCreationForm):
    error_messages = {
        'password_mismatch': _('Введенные пароли не совпадают'),
        'invalid_username': _('Никнейм должен быть длиннее 3 символов - вы ввели %(value)s'),
        'invalid_last_name': _('Фамилия должна быть длиннее 3 символов - вы ввели %(value)s'),
        'invalid_first_name': _('Имя должно быть длиннее 3 символов - вы ввели %(value)s'),
        'only_digits': _('Имя, никнейм и фамилия не могут являться числом'),
    }

    class Meta:
        model = MyUser
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2',)

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Введите имя пользователя'
        self.fields['email'].widget.attrs['placeholder'] = 'Введите адрес эл.почты'
        self.fields['first_name'].widget.attrs['placeholder'] = 'Введите имя'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Введите фамилию'
        self.fields['password1'].widget.attrs['placeholder'] = 'Введите пароль'
        self.fields['password2'].widget.attrs['placeholder'] = 'Подтвердите пароль'
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control py-4'

    def clean_username(self):
        username = len_validation(self, self.cleaned_data.get('username'), 'username')
        return username

    def clean_first_name(self):
        first_name = len_validation(self, self.cleaned_data.get('first_name'), 'first_name')
        return first_name

    def clean_last_name(self):
        last_name = len_validation(self, self.cleaned_data.get('last_name'), 'last_name')
        return last_name

    def save(self, commit=True):
        user = super().save()
        user.is_active = False
        salt = hashlib.sha1(str(random()).encode('utf8')).hexdigest()[:6]
        user.activation_key = hashlib.sha1((user.email + salt).encode('utf8')).hexdigest()
        user.save()
        return user


class UserProfileForm(UserChangeForm):
    img = forms.ImageField(widget=forms.FileInput(), required=False)

    class Meta:
        model = MyUser
        fields = ('username', 'email', 'first_name', 'last_name', 'img', 'score')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['readonly'] = True
        self.fields['email'].widget.attrs['readonly'] = True

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control py-4'
        self.fields['img'].widget.attrs['class'] = 'custom-file-input'


class UserChangeProfileForm(UserChangeForm):
    class Meta:
        model = MyUser
        fields = ('first_name', 'last_name', 'img')

    def __init__(self, *args, **kwargs):
        super(UserChangeProfileForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control py-4'


class UserImgChangeProfileForm(UserChangeForm):
    img = forms.ImageField(widget=forms.FileInput(), required=False)

    class Meta:
        model = MyUser
        fields = ('img',)

    def __init__(self, *args, **kwargs):
        super(UserImgChangeProfileForm, self).__init__(*args, **kwargs)

        self.fields['img'].widget.attrs['class'] = 'form-control'
        self.fields['img'].widget.attrs['id'] = 'avatar'


class WriteAdminForm(forms.Form):
    title = forms.CharField(max_length=255, label='Заголовок сообщения')
    content = forms.CharField(widget=forms.Textarea(attrs={'cols': 60, 'rows': 10}), label='Текст сообщения')
    grade = forms.IntegerField(min_value=1, max_value=10, label='Поставьте оценку нашему сайту от 1 до 10')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control py-4'


class MyPasswordResetForm(PasswordResetForm):
    error_messages = {
        'invalid_email': _('Пожалуйста, введите верный email. Введенный вами email не связан с аккаунтом'),
    }

    class Meta:
        model = MyUser
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['email'].widget.attrs['placeholder'] = 'Введите ваш email'
        self.fields['email'].widget.attrs['class'] = 'form-control py-4'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            MyUser.objects.get(email=email)
        except Exception:
            logger.warning('Попытка восстановления пароля на незарегистрированный email')
            msg = ValidationError(self.error_messages['invalid_email'], code='invalid_email')
            self.add_error('email', msg)
        return email
