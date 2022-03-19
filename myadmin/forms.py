from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from posts.models import Post
from questions.models import QuestionCategory, Question
from users.forms import UserRegisterForm, UserProfileForm
from users.models import MyUser


class UserAdminRegisterForm(UserRegisterForm):
    img = forms.ImageField(widget=forms.FileInput, required=False)

    class Meta:
        model = MyUser
        fields = ('username', 'first_name', 'last_name', 'email',
                  'password1', 'password2', 'img',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'img':
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-control py-4'


class UserAdminProfileForm(UserProfileForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['readonly'] = False
        self.fields['email'].widget.attrs['readonly'] = False

        for field_name, field in self.fields.items():
            if field_name == 'img':
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-control py-4'


class CategoryForm(ModelForm):
    image = forms.ImageField(widget=forms.FileInput, required=False)

    class Meta:
        model = QuestionCategory
        fields = ['name', 'description', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control py-4'
        self.fields['image'].widget.attrs['class'] = 'form-control'


class QuestionForm(ModelForm):
    error_messages = {
        'invalid_answer': _('Вы указали %(value)s как правильный ответ, но он не совпадает ни с одним '
                            'из предлагаемых вариантов ответа на вопрос'),
    }

    subject = forms.ModelChoiceField(queryset=QuestionCategory.objects.filter(available=True).select_related(),
                                     empty_label=None)
    image_01 = forms.ImageField(widget=forms.FileInput, required=False)
    image_02 = forms.ImageField(widget=forms.FileInput, required=False)
    image_03 = forms.ImageField(widget=forms.FileInput, required=False)

    class Meta:
        model = Question

        fields = ['question', 'subject', 'right_answer', 'answer_01', 'answer_02',
                  'answer_03', 'answer_04', 'difficulty_level', 'tag', 'image_01',
                  'image_02', 'image_03']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'image_01' \
                    or field_name == 'image_02' \
                    or field_name == 'image_03' \
                    or field_name == 'subject' \
                    or field_name == 'difficulty_level':
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-control py-4'

    def clean(self):
        answer = self.cleaned_data.get('right_answer')
        a1 = self.cleaned_data.get('answer_01')
        a2 = self.cleaned_data.get('answer_02')
        a3 = self.cleaned_data.get('answer_03')
        a4 = self.cleaned_data.get('answer_04')
        if answer != a1 and answer != a2 and answer != a3 and answer != a4:
            msg = ValidationError(self.error_messages['invalid_answer'],
                                  code=f'invalid_answer',
                                  params={'value': answer})
            self.add_error('right_answer', msg)
        return self.cleaned_data


class PostForm(ModelForm):
    category = forms.ModelChoiceField(queryset=QuestionCategory.objects.filter(available=True).select_related(),
                                      empty_label=None)
    image = forms.ImageField(widget=forms.FileInput, required=False)

    class Meta:
        model = Post
        fields = ['title', 'author', 'category', 'body', 'image',
                  'available', 'tag']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'image' \
                    or field_name == 'category' \
                    or field_name == 'author':
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-control py-4'
