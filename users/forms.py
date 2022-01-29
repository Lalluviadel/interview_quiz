from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm

from users.models import MyUser


class UserLoginForm(AuthenticationForm):
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
