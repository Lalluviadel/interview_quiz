"""Contains forms used to create or modify user, category, question, or post objects in the admin panel.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from posts.models import Post
from questions.models import QuestionCategory, Question
from users.forms import UserRegisterForm, UserProfileForm
from users.models import MyUser


class UserAdminRegisterForm(UserRegisterForm):
    """Form for creating a user from the admin panel.
    """
    img = forms.ImageField(widget=forms.FileInput, required=False)

    class Meta:
        """Defines the model involved and the fields used in the form.
        """
        model = MyUser
        fields = ('username', 'first_name', 'last_name', 'email',
                  'password1', 'password2', 'img',)

    def __init__(self, *args, **kwargs):
        """Manages the classes of form fields for their correct display on the page.
        """
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'img':
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-control py-4'


class UserAdminProfileForm(UserProfileForm):
    """Form for editing a user profile from the admin panel.
    """

    def __init__(self, *args, **kwargs):
        """Manages the classes of form fields for their correct display on the page.
        Allows editing of 'username' and 'email' fields that are initially in read-only mode.
        """
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['readonly'] = False
        self.fields['email'].widget.attrs['readonly'] = False

        for field_name, field in self.fields.items():
            if field_name == 'img':
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-control py-4'


class CategoryForm(ModelForm):
    """Form for creating and editing categories in the admin panel.
    """
    image = forms.ImageField(widget=forms.FileInput, required=False)

    class Meta:
        """Defines the model involved and the fields used in the form.
        """
        model = QuestionCategory
        fields = ['name', 'description', 'image']

    def __init__(self, *args, **kwargs):
        """Manages the classes of form fields for their correct display on the page.
        """
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control py-4'
        self.fields['image'].widget.attrs['class'] = 'form-control'


class QuestionForm(ModelForm):
    """Form for creating and editing questions in the admin panel.
    """
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
        """Defines the model involved and the fields used in the form.
        """
        model = Question
        fields = ['question', 'subject', 'right_answer', 'answer_01', 'answer_02',
                  'answer_03', 'answer_04', 'difficulty_level', 'tag', 'image_01',
                  'image_02', 'image_03']

    def __init__(self, *args, **kwargs):
        """Manages the classes of form fields for their correct display on the page.
        """
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name in ['image_01', 'image_02', 'image_03', 'subject', 'difficulty_level']:
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-control py-4'
        for item in ('image_01', 'image_02', 'image_03'):
            self.fields[item].widget.attrs['id'] = f'{item}'

    def clean(self):
        """Checks whether the correct answer matches one of the 4 options
        for user responses, if not, adds in form an error message, which will
        be displayed on the page to inform the user.
        """
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
    """Form for creating and editing posts in the admin panel.
    """
    category = forms.ModelChoiceField(queryset=QuestionCategory.objects.filter(available=True).select_related(),
                                      empty_label=None)
    image = forms.ImageField(widget=forms.FileInput, required=False)

    class Meta:
        """Defines the model involved and the fields used in the form.
        """
        model = Post
        fields = ['title', 'category', 'body', 'image',
                  'available', 'tag']

    def __init__(self, *args, **kwargs):
        """Manages the classes of form fields for their correct display on the page.
        """
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'image' or field_name == 'category':
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-control py-4'
        self.fields['image'].widget.attrs['id'] = 'post_image'
