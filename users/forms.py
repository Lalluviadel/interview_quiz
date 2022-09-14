"""
Contains forms for registration and authorization of the user, recovery of his password.
To manage the user's profile, forms are implemented in which he can change some of his data,
as well as change his avatar. In addition, there is a form for writing a message to the admin.
"""
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
    """Checks the data length of the specified field.
    If the length is less than 3 characters, it adds an error message to the form.
    Next, it runs the following field check to see if the data entered by the user contains only numbers.

    Args:

        * obj (`RegistrationForm` or `UserChangeProfileForm`): form instance;
        * field (`str`): data of the field being checked;
        * field_name (`str`): name of the field to be checked;

    Returns:

        * field(`str`): name of the field to be checked.
    """
    name_len = len(field)
    if name_len <= 3:
        msg = ValidationError(obj.error_messages[f'invalid_{field_name}'],
                              code=f'invalid_{field_name}',
                              params={'value': name_len})
        obj.add_error(f'{field_name}', msg)
    num_validation(obj, field, field_name)
    return field


def num_validation(obj, field, field_name):
    """Checks whether only numbers have been entered in the form field.
    This allows you to prevent the registration of users who have entered numbers
    instead of a name, username or surname.

    Args:

        * obj (`RegistrationForm`): form instance;
        * field (`str`): data of the field being checked;
        * field_name (`str`): name of the field to be checked;

    Returns:

        * field(`str`): name of the field to be checked.
    """
    if field.isdigit():
        msg = ValidationError(obj.error_messages['only_digits'],
                              code='only_digits', )
        obj.add_error(f'{field_name}', msg)
    return field


class UserLoginForm(AuthenticationForm):
    """A form for authorization of registered users.
    """
    error_messages = {
        'invalid_login': _(
            "Пожалуйста, введите верный логин и пароль с учетом регистра"
        ),
    }

    class Meta:
        """Defines the model involved and the fields used in the form.
        """
        model = MyUser
        fields = ('username', 'password')

    def __init__(self, *args, **kwargs):
        """Manages the classes of form fields for their correct display on the page.
        Sets placeholders for form fields.
        """
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Введите имя пользователя'
        self.fields['password'].widget.attrs['placeholder'] = 'Введите пароль'
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control py-4'


class UserRegisterForm(UserCreationForm):
    """A form for registering new users."""
    error_messages = {
        'password_mismatch': _('Введенные пароли не совпадают'),
        'invalid_username': _('Никнейм должен быть длиннее 3 символов - вы ввели %(value)s'),
        'invalid_last_name': _('Фамилия должна быть длиннее 3 символов - вы ввели %(value)s'),
        'invalid_first_name': _('Имя должно быть длиннее 3 символов - вы ввели %(value)s'),
        'only_digits': _('Имя, никнейм и фамилия не могут являться числом'),
    }

    class Meta:
        """Defines the model involved and the fields used in the form.
        """
        model = MyUser
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2',)

    def __init__(self, *args, **kwargs):
        """Manages the classes of form fields for their correct display on the page.
        Sets placeholders for form fields.
        """
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
        """Checks the data in the username field (for their length and whether it contains only numbers)."""
        username = len_validation(self, self.cleaned_data.get('username'), 'username')
        return username

    def clean_first_name(self):
        """Checks the data in the firstname field (for their length and whether it contains only numbers)."""
        first_name = len_validation(self, self.cleaned_data.get('first_name'), 'first_name')
        return first_name

    def clean_last_name(self):
        """Checks the data in the lastname field (for their length and whether it contains only numbers)."""
        last_name = len_validation(self, self.cleaned_data.get('last_name'), 'last_name')
        return last_name

    def save(self, commit=True):
        """When saving the form, an activation key is generated to confirm the registration of a new user.
        The user will remain inactive until the moment of clicking on the link from the email sent to his mail."""
        user = super().save()
        user.is_active = False
        salt = hashlib.sha1(str(random()).encode('utf8')).hexdigest()[:6]
        user.activation_key = hashlib.sha1((user.email + salt).encode('utf8')).hexdigest()
        user.save()
        return user


class UserProfileForm(UserChangeForm):
    """The form has two purposes: in the admin panel it is used to edit user data,
    and in the main part it is necessary for the user to view his profile.
    The admin panel uses a child class of this form.
    """
    img = forms.ImageField(widget=forms.FileInput(), required=False)

    class Meta:
        """Defines the model involved and the fields used in the form.
        """
        model = MyUser
        fields = ('username', 'email', 'first_name', 'last_name', 'img', 'score')

    def __init__(self, *args, **kwargs):
        """Manages the classes of form fields for their correct display on the page.
        Sets the read-only mode for the username and email fields to prohibit editing them.
        """
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['readonly'] = True
        self.fields['email'].widget.attrs['readonly'] = True

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control py-4'
        self.fields['img'].widget.attrs['class'] = 'custom-file-input'


class UserChangeProfileForm(UserChangeForm):
    """A form for the user to edit his profile."""
    error_messages = {
        'invalid_last_name': _('Фамилия должна быть длиннее 3 символов - вы ввели %(value)s'),
        'invalid_first_name': _('Имя должно быть длиннее 3 символов - вы ввели %(value)s'),
        'only_digits': _('Имя, никнейм и фамилия не могут являться числом'),
    }

    class Meta:
        """Defines the model involved and the fields used in the form.
        """
        model = MyUser
        fields = ('first_name', 'last_name', 'img')

    def __init__(self, *args, **kwargs):
        """Manages the classes of form fields for their correct display on the page.
        """
        super(UserChangeProfileForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control py-4'
            try:
                if kwargs['instance'].social_network:
                    field.widget.attrs.update({'disabled': 'disabled'})
            except Exception:
                logger.error('Ошибка дезактивации полей формы редактирования профиля для профиля из соцсетей.')

    def clean_first_name(self):
        """Checks the data in the firstname field (for their length and whether it contains only numbers)."""
        first_name = len_validation(self, self.cleaned_data.get('first_name'), 'first_name')
        return first_name

    def clean_last_name(self):
        """Checks the data in the lastname field (for their length and whether it contains only numbers)."""
        last_name = len_validation(self, self.cleaned_data.get('last_name'), 'last_name')
        return last_name


class UserImgChangeProfileForm(UserChangeForm):
    """A form for the user to edit his avatar."""
    img = forms.ImageField(widget=forms.FileInput(), required=False)

    class Meta:
        """Defines the model involved and the fields used in the form.
        """
        model = MyUser
        fields = ('img',)

    def __init__(self, *args, **kwargs):
        """Manages the class and id of form field img for its correct display on the page.
        """
        super(UserImgChangeProfileForm, self).__init__(*args, **kwargs)
        self.fields['img'].widget.attrs['class'] = 'form-control'
        self.fields['img'].widget.attrs['id'] = 'avatar'


class WriteAdminForm(forms.Form):
    """A form for the user to write a message for the admin."""
    title = forms.CharField(max_length=255, label='Заголовок сообщения')
    content = forms.CharField(widget=forms.Textarea(attrs={'cols': 60, 'rows': 10}), label='Текст сообщения')
    grade = forms.IntegerField(min_value=1, max_value=10, label='Поставьте оценку нашему сайту от 1 до 10')

    def __init__(self, *args, **kwargs):
        """Manages the classes of form fields for their correct display on the page.
        """
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control py-4'


class MyPasswordResetForm(PasswordResetForm):
    """A form for user password recovery."""
    error_messages = {
        'invalid_email': _('Пожалуйста, введите верный email. Введенный вами email не связан с аккаунтом'),
    }

    class Meta:
        """Defines the model involved and the fields used in the form.
        """
        model = MyUser
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        """Manages the class and placeholder of email form field for its correct display on the page.
        """
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = 'Введите ваш email'
        self.fields['email'].widget.attrs['class'] = 'form-control py-4'

    def clean_email(self):
        """Checks whether the email address that the user specified for password recovery was used for registration."""
        email = self.cleaned_data.get('email')
        try:
            MyUser.objects.get(email=email)
        except Exception:
            logger.warning('Попытка восстановления пароля на незарегистрированный email')
            msg = ValidationError(self.error_messages['invalid_email'], code='invalid_email')
            self.add_error('email', msg)
        return email
