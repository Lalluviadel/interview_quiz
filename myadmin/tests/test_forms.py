import logging
import sys

from django.test import SimpleTestCase, TestCase

from ..forms import UserAdminRegisterForm, UserAdminProfileForm, CategoryForm, QuestionForm, PostForm
from users.models import MyUser
from questions.models import QuestionCategory, Question
from posts.models import Post

if len(sys.argv) > 1 and sys.argv[1] == 'test':
    logging.disable(logging.CRITICAL)


class TestUserAdminRegisterForm(TestCase):
    """Test for the UserAdminRegisterForm form"""

    def setUp(self):
        """Initializing data for the form"""
        self.form_data = {
            'username': 'PyQT',
            'first_name': 'Quentin',
            'last_name': 'Tarantino',
            'email': 'quieteen@mail.ru',
            'password1': 'QwEnTeEn123',
            'password2': 'QwEnTeEn123',
        }

    def test_admin_user_register_form_fields_class(self):
        """Checks the classes and the composition of form fields for their correct display in HTML"""
        form = UserAdminRegisterForm()
        fields = []
        for field_name, field in form.fields.items():
            if field_name == 'img':
                self.assertTrue(field.widget.attrs['class'], 'form-control')
            else:
                self.assertTrue(field.widget.attrs['class'], 'form-control py-4')
            fields.append(field_name)
        self.assertListEqual(fields, ['username', 'first_name', 'last_name', 'email',
                                      'password1', 'password2', 'img', ])

    def test_admin_user_create(self):
        """Form health test and verification of the creation of a new record"""
        form = UserAdminRegisterForm(data=self.form_data)
        form.is_valid()
        form.save()
        self.assertTrue(MyUser.objects.filter(email=self.form_data['email']).count() == 1)

    class TestUserAdminRegisterForm(TestCase):
        """Test for the UserAdminRegisterForm form"""

        def setUp(self):
            """Initializing data for the form"""
            self.form_data = {
                'username': 'PyQT',
                'first_name': 'Quentin',
                'last_name': 'Tarantino',
                'email': 'quieteen@mail.ru',
                'password1': 'QwEnTeEn123',
                'password2': 'QwEnTeEn123',
            }

        def test_user_admin_register_form_fields_class(self):
            """Checking the classes of form fields for their correct display in HTML"""
            form = UserAdminRegisterForm()
            for field_name, field in form.fields.items():
                if field_name == 'img':
                    self.assertTrue(field.widget.attrs['class'], 'form-control')
                else:
                    self.assertTrue(field.widget.attrs['class'], 'form-control py-4')

        def test_admin_user_created(self):
            """Form health test and verification of the creation of a new record"""
            form = UserAdminRegisterForm(data=self.form_data)
            form.is_valid()
            form.save()
            self.assertTrue(MyUser.objects.filter(email=self.form_data['email']).count() == 1)


class TestUserAdminProfileForm(SimpleTestCase):
    """Test for the UserAdminProfileForm form"""
    def test_admin_user_profile_form_fields_readonly(self):
        """Checks that individual not editable fields are editable in the admin panel"""
        form = UserAdminProfileForm()
        self.assertFalse(form.fields['username'].widget.attrs['readonly'])
        self.assertFalse(form.fields['email'].widget.attrs['readonly'])

    def test_admin_user_profile_form_fields_class(self):
        """Checks the classes of form fields for their correct display in HTML"""
        form = UserAdminProfileForm()
        for field_name, field in form.fields.items():
            if field_name == 'img':
                self.assertTrue(field.widget.attrs['class'], 'form-control')
            else:
                self.assertTrue(field.widget.attrs['class'], 'form-control py-4')


class TestCategoryForm(TestCase):
    """Test for the CategoryForm form"""

    def setUp(self):
        """Initializing data for the form"""
        self.form_data = {
            'name': 'Python',
            'description': 'some text',
        }

    def test_admin_category_form_fields_class(self):
        """Checks the classes and the composition of form fields for their correct display in HTML"""
        form = CategoryForm()
        fields = []
        for field_name, field in form.fields.items():
            if field_name == 'image':
                self.assertTrue(field.widget.attrs['class'], 'form-control')
            else:
                self.assertTrue(field.widget.attrs['class'], 'form-control py-4')
            fields.append(field_name)
        self.assertListEqual(fields, ['name', 'description', 'image'])

    def test_admin_category_create(self):
        """Form health test and verification of the creation of a new record"""
        form = CategoryForm(data=self.form_data)
        form.is_valid()
        form.save()
        self.assertTrue(QuestionCategory.objects.filter(name=self.form_data['name']).count() == 1)


class TestQuestionForm(TestCase):
    """Test for the QuestionForm form"""

    def setUp(self):
        """Initializing data for the form"""
        self.test_user = MyUser.objects.create_user(username='drf',
                                                    first_name='Roland',
                                                    last_name='Emmerich',
                                                    email='blabla@bla.ru')
        self.test_user.set_password('laLA12')
        self.test_user.save()
        self.test_category = QuestionCategory.objects.create(name='Философия жизни')
        self.form_data = {
            'question': 'В чем сила, брат?',
            'subject': self.test_category,
            'right_answer': 'Сила в правде',
            'answer_01': 'Сила в деньгах',
            'answer_02': 'Сила во власти',
            'answer_03': 'Сила в правде',
            'answer_04': 'Сила в свободе',
            'difficulty_level': 'NB',
            'tag': 'Классика',
        }

    def test_admin_question_form_fields_class(self):
        """Checks the classes and the composition of form fields for their correct display in HTML"""
        form = QuestionForm()
        fields = []
        for field_name, field in form.fields.items():
            if field_name in ['image_01', 'image_02', 'image_03', 'subject', 'difficulty_level']:
                self.assertTrue(field.widget.attrs['class'], 'form-control')
            else:
                self.assertTrue(field.widget.attrs['class'], 'form-control py-4')
            fields.append(field_name)
        self.assertListEqual(fields, ['question', 'subject', 'right_answer', 'answer_01', 'answer_02',
                                      'answer_03', 'answer_04', 'difficulty_level', 'tag', 'image_01',
                                      'image_02', 'image_03'])

    def test_admin_question_create(self):
        """Form health test and verification of the creation of a new record."""
        form = QuestionForm(data=self.form_data)
        form.is_valid()
        question = form.save(commit=False)
        question.author = self.test_user
        question.save()
        self.assertTrue(Question.objects.filter(question=self.form_data['question']).count() == 1)

    def test_admin_question_create_no_right_answer_error(self):
        """A test to check the transmission of an error to the form that the correct answer
        does not match any of the answer options"""

        no_right_answer_data = self.form_data
        no_right_answer_data['right_answer'] = "text that doesn't match any of answers"
        form = QuestionForm(data=no_right_answer_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['right_answer'][0], "Вы указали text that doesn't match any of answers "
                                                         "как правильный ответ, но он не совпадает ни с одним из "
                                                         "предлагаемых вариантов ответа на вопрос")


class TestPostForm(TestCase):
    """Test for the PostForm form"""

    def setUp(self):
        """Initializing data for the form"""
        self.test_user = MyUser.objects.create_user(username='drf',
                                                    first_name='Roland',
                                                    last_name='Emmerich',
                                                    email='blabla@bla.ru')
        self.test_user.set_password('laLA12')
        self.test_user.save()
        self.test_category = QuestionCategory.objects.create(name='Философия жизни')
        self.form_data = {
            'title': 'В чем сила, брат?',
            'category': self.test_category,
            'body': 'Сила в правде',
            'available': True,
            'tag': 'Классика',
        }

    def test_admin_post_form_fields_class(self):
        """Checks the classes and the composition of form fields for their correct display in HTML"""
        form = PostForm()
        fields = []
        for field_name, field in form.fields.items():
            if field_name == 'image' or field_name == 'category':
                self.assertTrue(field.widget.attrs['class'], 'form-control')
            else:
                self.assertTrue(field.widget.attrs['class'], 'form-control py-4')
            fields.append(field_name)
        self.assertListEqual(fields, ['title', 'category', 'body', 'image', 'available', 'tag'])

    def test_admin_post_create(self):
        """Form health test and verification of the creation of a new record."""
        form = PostForm(data=self.form_data)
        form.is_valid()
        post = form.save(commit=False)
        post.author = self.test_user
        post.save()
        self.assertTrue(Post.objects.filter(title=self.form_data['title']).count() == 1)
