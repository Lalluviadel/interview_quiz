"""
Contains unit and integration tests for checking the views of the web application.
"""
import logging
import sys
from datetime import timedelta

from django.test import TestCase, Client, SimpleTestCase
from django.urls import reverse
from django.utils.timezone import now

from interview_quiz.settings import EMAIL_HOST_USER
from posts.models import Post
from questions.models import QuestionCategory, Question
from ..forms import UserLoginForm, UserRegisterForm
from ..models import MyUser

if len(sys.argv) > 1 and sys.argv[1] == 'test':
    logging.disable(logging.CRITICAL)


class TestUserBase(TestCase):
    """Parent class for preparing data for testing and observing the DRY pattern."""

    def setUp(self):
        """Creating and preparing a user test object."""
        self.client = Client()
        self.test_user = MyUser.objects.create_user(username='test', email=EMAIL_HOST_USER)
        self.test_user.set_password('laLA12')
        self.test_user.is_active = True
        self.test_user.save()
        self.client.login(username=self.test_user.username, password='laLA12')


class TestUserCategoryBase(TestUserBase):
    """Parent class for test classes that require a prepared test category."""

    def setUp(self):
        """Creating and preparing a test category."""
        super().setUp()
        self.category = QuestionCategory.objects.create(name='TestCategory', description='test')
        self.category.available = True
        self.category.save()


class TestAnonymousAndAuthorizedUser(TestCase):
    """Testing access only for authorized users."""

    def setUp(self):
        """Creating and preparing a user test object."""
        self.client = Client()
        self.test_user = MyUser.objects.create_user(username='test', email='test1@mail.ru')
        self.test_user.set_password('laLA12')
        self.test_user.is_active = True
        self.test_user.save()

    def test_profile_login_redirect(self):
        """Testing the unavailability of the profile page without user authorization."""
        response = self.client.get('/users/profile/')
        self.assertEqual(response.url, '/users/login/?next=/users/profile/')
        self.assertEqual(response.status_code, 302)

    def test_profile_ok(self):
        """Testing the availability of the profile page when the user is logged in."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/users/profile/')
        self.assertEqual(response.request['PATH_INFO'], '/users/profile/')
        self.assertEqual(response.status_code, 200)

    def test_post_create_login_redirect(self):
        """Testing the unavailability of the post creation page without user authorization."""
        response = self.client.get('/users/posts_create/')
        self.assertEqual(response.url, '/users/login/?next=/users/posts_create/')
        self.assertEqual(response.status_code, 302)

    def test_post_create_ok(self):
        """Testing the availability of the post creation page when the user is logged in."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/users/posts_create/')
        self.assertEqual(response.request['PATH_INFO'], '/users/posts_create/')
        self.assertEqual(response.status_code, 200)

    def test_question_create_login_redirect(self):
        """Testing the unavailability of the question creation page without user authorization."""
        response = self.client.get('/users/question_create/')
        self.assertEqual(response.url, '/users/login/?next=/users/question_create/')
        self.assertEqual(response.status_code, 302)

    def test_question_create_ok(self):
        """Testing the availability of the question creation page when the user is logged in."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/users/question_create/')
        self.assertEqual(response.request['PATH_INFO'], '/users/question_create/')
        self.assertEqual(response.status_code, 200)

    def test_top_users_login_redirect(self):
        """Testing the unavailability of the Top 5 participants' page without user authorization."""
        response = self.client.get('/users/top_users/')
        self.assertEqual(response.url, '/users/login/?next=/users/top_users/')
        self.assertEqual(response.status_code, 302)

    def test_top_users_ok(self):
        """Testing the availability of the Top 5 participants' page when the user is logged in."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/users/top_users/')
        self.assertEqual(response.request['PATH_INFO'], '/users/top_users/')
        self.assertEqual(response.status_code, 200)

    def test_write_to_admin_login_redirect(self):
        """Testing the inaccessibility of the page for sending a message to the admin without user authorization."""
        response = self.client.get('/users/write_to_admin/')
        self.assertEqual(response.url, '/users/login/?next=/users/write_to_admin/')
        self.assertEqual(response.status_code, 302)

    def test_write_to_admin_ok(self):
        """Testing the availability of the page for sending a message to the admin when the user is logged in."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/users/write_to_admin/')
        self.assertEqual(response.request['PATH_INFO'], '/users/write_to_admin/')
        self.assertEqual(response.status_code, 200)


class TestUserLoginView(TestCase):
    """Testing the user authorization process."""

    def setUp(self):
        """Creating and preparing a user test object."""
        self.client = Client()
        self.test_user = MyUser.objects.create_user(username='test', email='test1@mail.ru')
        self.test_user.set_password('laLA12')
        self.test_user.is_active = True
        self.test_user.save()

    def test_login_unsuccessful(self):
        """Testing a failed authorization attempt."""
        response = self.client.post(path='/users/login/', data={'username': 'not_exist', 'password': 'not_exist'})
        self.assertEqual(response.context['form'].__class__, UserLoginForm().__class__)
        self.assertFormError(response, 'form', '__all__', 'Пожалуйста, введите верный логин и пароль с учетом регистра')

    def test_login_ok(self):
        """Testing a successful authorization attempt."""
        response = self.client.post(path='/users/login/', data={'username': 'test', 'password': 'laLA12'})
        self.assertRedirects(response, reverse('index'))
        response_to_profile = self.client.get(reverse('users:profile'))
        self.assertEqual(response_to_profile.status_code, 200)


class TestUserRegisterView(TestCase):
    """Testing the process of registering a new user."""

    def setUp(self):
        """Preparation of data for testing registration."""
        self.client = Client()
        self.test_data = {'username': 'test',
                          'email': EMAIL_HOST_USER,
                          'first_name': 'Quentin',
                          'last_name': 'Tarantino',
                          'password1': 'TeSt123Qwe))',
                          'password2': 'TeSt123Qwe))',
                          }

    def test_register_ok(self):
        """Testing the successful registration process."""
        response = self.client.post(path='/users/register/', data=self.test_data)
        self.assertRedirects(response, reverse('users:register'))
        self.assertTrue(response.context['my_link'])

    def test_register_unsuccessful_passwords(self):
        """Testing an unsuccessful registration process: mismatch of the entered passwords."""
        test_data = self.test_data
        test_data['password1'] = '123456'
        response = self.client.post(path='/users/register/', data=test_data)
        self.assertEqual(response.context['form'].__class__, UserRegisterForm().__class__)
        self.assertFormError(response, 'form', 'password2', 'Введенные пароли не совпадают')

    def test_register_unsuccessful_short_username(self):
        """Testing a failed registration process: the username is too short (less than 4 characters)."""
        test_data = self.test_data
        test_data['username'] = 'QWe'
        response = self.client.post(path='/users/register/', data=test_data)
        self.assertFormError(response, 'form', 'username', 'Никнейм должен быть длиннее 3 символов - вы ввели 3')

    def test_register_unsuccessful_short_last_name(self):
        """Testing a failed registration process: the lastname is too short (less than 4 characters)."""
        test_data = self.test_data
        test_data['last_name'] = 'QWe'
        response = self.client.post(path='/users/register/', data=test_data)
        self.assertFormError(response, 'form', 'last_name', 'Фамилия должна быть длиннее 3 символов - вы ввели 3')

    def test_register_unsuccessful_short_first_name(self):
        """Testing a failed registration process: the firstname is too short (less than 4 characters)."""
        test_data = self.test_data
        test_data['first_name'] = 'QWe'
        response = self.client.post(path='/users/register/', data=test_data)
        self.assertFormError(response, 'form', 'first_name', 'Имя должно быть длиннее 3 символов - вы ввели 3')

    def test_register_unsuccessful_num_first_name(self):
        """Testing a failed registration process: the firstname consists only of digits."""
        test_data = self.test_data
        test_data['first_name'] = '123123'
        response = self.client.post(path='/users/register/', data=test_data)
        self.assertFormError(response, 'form', 'first_name', 'Имя, никнейм и фамилия не могут являться числом')


class TestVerifyView(TestCase):
    """Testing the verification of a new profile."""

    def setUp(self):
        """Creating and preparing a user test object."""
        self.client = Client()
        self.test_user = MyUser.objects.create_user(username='test', email='test1@mail.ru')
        self.test_user.set_password('laLA12')
        self.test_user.activation_key = '1234qwerty1234'
        self.test_user.activation_key_created = now()
        self.test_user.save()

    def test_verify_ok(self):
        """Testing the successful verification process of the new profile."""
        response = self.client.get(reverse('users:verify', kwargs={'email': self.test_user.email,
                                                                   'activation_key': self.test_user.activation_key}))
        self.assertTrue(response.context['user'].is_active)
        self.assertFalse(response.context['user'].activation_key)
        self.assertFalse(response.context['user'].activation_key_created)
        self.assertTemplateUsed(response, 'registration/verification.html')

        response = self.client.get('/users/profile/')
        self.assertEqual(response.status_code, 200)

    def test_verify_wrong_email(self):
        """Testing a failed verification process for a new profile: incorrect email."""
        response = self.client.get(reverse('users:verify', kwargs={'email': 'test_email@mail.ru',
                                                                   'activation_key': self.test_user.activation_key}))
        msg = f'Сбой активации. Попробуйте использовать ссылку, полученную в письме, повторною. ' \
              f'В случае неудачи напишите на адрес {EMAIL_HOST_USER}, указав причину обращения.'
        self.assertRedirects(response, reverse('users:failed', kwargs={'error': msg}))

    def test_verify_wrong_activation_key(self):
        """Testing a failed verification process for a new profile: incorrect activation key."""
        response = self.client.get(reverse('users:verify', kwargs={'email': self.test_user.email,
                                                                   'activation_key': '345122fffdsgg'}))
        msg = f'Сбой активации. Попробуйте использовать ссылку, полученную в письме, повторною. ' \
              f'В случае неудачи напишите на адрес {EMAIL_HOST_USER}, указав причину обращения.'
        self.assertRedirects(response, reverse('users:failed', kwargs={'error': msg}))

    def test_verify_activation_key_is_expired(self):
        """Testing a failed verification process for a new profile: the activation key has expired."""
        self.test_user = self.test_user
        self.test_user.activation_key_created -= timedelta(hours=48)
        self.test_user.save()
        response = self.client.get(reverse('users:verify', kwargs={'email': self.test_user.email,
                                                                   'activation_key': self.test_user.activation_key}))
        msg = f'Ваш ключ активации устарел. ' \
              f'Для активации вашего профиля напишите письмо на адрес {EMAIL_HOST_USER} ' \
              f'или зарегистрируйте новый профиль, используя другой email.'
        self.assertRedirects(response, reverse('users:failed', kwargs={'error': msg}))


class TestFailedAuthenticationView(SimpleTestCase):
    """Testing the view of the notification page about unsuccessful profile verification."""

    def test_failed_auth_transition(self):
        """Testing the view of the notification page about unsuccessful profile verification."""
        client = Client()
        response = client.get(reverse('users:failed', kwargs={'error': 'Пример ошибки'}))
        self.assertEqual(response.context['title'], 'Неудачная авторизация')
        self.assertTemplateUsed(response, 'registration/attempt_failed.html')


class TestUserLogoutView(TestCase):
    """Testing the user's logout."""

    def setUp(self):
        """Creating and preparing a user text object."""
        self.client = Client()
        self.test_user = MyUser.objects.create_user(username='test', email='test1@mail.ru')
        self.test_user.set_password('laLA12')
        self.test_user.is_active = True
        self.test_user.save()
        self.client.login(username=self.test_user.username, password='laLA12')

    def test_logout(self):
        """Testing the process of logging out of the user profile."""
        response = self.client.get('/users/profile/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('users:logout'))
        self.assertRedirects(response, reverse('index'))
        response = self.client.get('/users/profile/')
        self.assertEqual(response.status_code, 302)


class TestUserPasswordResetView(TestCase):
    """Testing the process of requesting a new password."""

    def setUp(self):
        """Creating and preparing a user text object."""
        self.client = Client()
        self.test_user = MyUser.objects.create_user(username='test', email=EMAIL_HOST_USER)
        self.test_user.set_password('laLA12')
        self.test_user.is_active = True
        self.test_user.save()

    def test_password_reset_ok(self):
        """Testing the successful completion of the process of requesting a new password."""
        response = self.client.post(path='/users/password_reset/', data={'email': self.test_user.email})
        self.assertTemplateUsed(response, 'registration/password_reset_email_sent.html')
        self.assertTrue(response.context['token'])

    def test__password_reset_wrong_email(self):
        """Testing the unsuccessful completion of the process of requesting a new password: incorrect email."""
        response = self.client.post(path='/users/password_reset/', data={'email': 'not_exist@not_exist.ru'})
        self.assertFalse(response.context['form'].is_valid())
        self.assertFormError(response, 'form', 'email', 'Введите правильный адрес электронной почты.')


class TestMyPasswordResetConfirmView(TestCase):
    """Testing the password change process."""

    def setUp(self):
        """Creating and preparing a user text object."""
        self.client = Client()
        self.test_user = MyUser.objects.create_user(username='test', email=EMAIL_HOST_USER)
        self.test_user.set_password('laLA12')
        self.test_user.is_active = True
        self.test_user.save()

    def test_password_reset_confirm_ok(self):
        """Testing the successful completion of the password change process."""
        response = self.client.post(path='/users/password_reset/', data={'email': self.test_user.email})
        uid, token = response.context['uid'], response.context['token']

        response = self.client.get(reverse('users:password_reset_confirm', kwargs={'token': token, 'uidb64': uid}))
        response_reset = self.client.post(path=response.url,
                                          data={'new_password1': 'La12LaLA222', 'new_password2': 'La12LaLA222'})
        self.assertRedirects(response_reset, reverse('users:password_reset_complete'))

        user_reset_pswd = MyUser.objects.get(id=self.test_user.id)
        self.assertNotEquals(self.test_user.password, user_reset_pswd.password)


class TestMyPasswordResetCompleteView(SimpleTestCase):
    """Testing the completion of the password recovery process."""

    def test_password_reset_complete_ok(self):
        """Testing the successful completion of the password recovery process."""
        client = Client()
        response = client.get(reverse('users:password_reset_complete'))
        self.assertEqual(response.context['title'], 'Пароль успешно изменен')
        self.assertTemplateUsed(response, 'registration/password_res_complete.html')


class TestProfileView(TestUserBase):
    """Testing the view to display the user profile."""

    def setUp(self):
        """Creating and preparing a user text object."""
        super().setUp()

    def test_profile_user(self):
        """Testing access to the user profile page."""
        response = self.client.get('/users/profile/')
        self.assertEqual(response.request['PATH_INFO'], '/users/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['title'], 'Мой профиль')


class TestUserEdit(TestUserBase):
    """Testing the user profile editing process."""

    def setUp(self):
        """Creating and preparing a user text object."""
        super().setUp()
        self.client.get(reverse('users:profile'))

    def test_user_edit_ok(self):
        """Testing a successful user profile editing process."""
        self.client.post(path='/users/profile_edit/', data={'first_name': 'Roland', 'last_name': 'Emmerich'})
        user = MyUser.objects.get(id=self.test_user.id)
        self.assertNotEquals(self.test_user.last_name, user.last_name)
        self.assertNotEquals(self.test_user.first_name, user.first_name)
        self.assertEqual(user.last_name, 'Emmerich')
        self.assertEqual(user.first_name, 'Roland')

    def test_user_edit_wrong_first_name_num(self):
        """Testing an unsuccessful user profile editing process: the firstname consists only of digits."""
        self.client.post(path='/users/profile_edit/', data={'first_name': '123', 'last_name': 'Emmerich'})
        user = MyUser.objects.get(id=self.test_user.id)
        self.assertEqual(self.test_user.last_name, user.last_name)
        self.assertNotEqual(user.last_name, 'Emmerich')
        self.assertEqual(self.test_user.first_name, user.first_name)
        self.assertNotEqual(user.first_name, '123')

    def test_user_edit_wrong_first_name_length(self):
        """Testing an unsuccessful user profile editing process: the firstname is too short (less than 4 characters)."""
        self.client.post(path='/users/profile_edit/', data={'first_name': 'Rol', 'last_name': 'Emmerich'})
        user = MyUser.objects.get(id=self.test_user.id)
        self.assertEqual(self.test_user.last_name, user.last_name)
        self.assertNotEqual(user.last_name, 'Emmerich')
        self.assertEqual(self.test_user.first_name, user.first_name)
        self.assertNotEqual(user.first_name, 'Rol')

    def test_user_edit_wrong_last_name_num(self):
        """Testing an unsuccessful user profile editing process: the lastname consists only of digits."""
        self.client.post(path='/users/profile_edit/', data={'first_name': 'Roland', 'last_name': '123'})
        user = MyUser.objects.get(id=self.test_user.id)
        self.assertEqual(self.test_user.last_name, user.last_name)
        self.assertNotEqual(user.last_name, '123')
        self.assertEqual(self.test_user.first_name, user.first_name)
        self.assertNotEqual(user.first_name, 'Roland')

    def test_user_edit_wrong_last_name_length(self):
        """Testing an unsuccessful user profile editing process: the lastname is too short (less than 4 characters)."""
        self.client.post(path='/users/profile_edit/', data={'first_name': 'Roland', 'last_name': 'Emm'})
        user = MyUser.objects.get(id=self.test_user.id)
        self.assertEqual(self.test_user.last_name, user.last_name)
        self.assertNotEqual(user.last_name, 'Emm')
        self.assertEqual(self.test_user.first_name, user.first_name)
        self.assertNotEqual(user.first_name, 'Roland')


class TestUserPostCreateView(TestUserCategoryBase):
    """Testing the creation of a new post by the user."""

    def setUp(self):
        """Preparing data for tests."""
        super().setUp()

        self.data = {
            'title': 'Test',
            'category': self.category.id,
            'body': 'test test test',
            'tag': 'test',
        }

    def test_user_post_create_ok(self):
        """Testing the successful creation of a new post by the user."""
        response = self.client.post(path='/users/posts_create/', data=self.data)
        self.assertTrue(Post.objects.get(title=self.data['title']))
        self.assertRedirects(response, reverse('users:profile'))
        self.assertEqual(self.test_user, Post.objects.get(title=self.data['title']).author)


class TestUserQuestionCreateView(TestUserCategoryBase):
    """Testing the creation of a new question by the user."""

    def setUp(self):
        """Preparing data for tests."""
        super().setUp()

        self.data = {
            'question': 'Test',
            'author': self.test_user.username,
            'subject': self.category.id,
            'right_answer': 'blabla',
            'answer_01': 'test test test',
            'answer_02': 'test test test',
            'answer_03': 'test test test',
            'answer_04': 'blabla',
            'difficulty_level': 'NB',
            'tag': 'test',
        }

    def test_user_question_create_ok(self):
        """Testing the successful creation of a new question by the user."""
        response = self.client.post(path='/users/question_create/', data=self.data)
        self.assertTrue(Question.objects.get(question=self.data['question']))
        self.assertRedirects(response, reverse('users:profile'))
        self.assertEqual(self.test_user, Question.objects.get(question=self.data['question']).author)

    def test_user_question_create_no_right_answer(self):
        """Testing the user's unsuccessful creation of a new question:
        the correct answer does not match any answer option."""
        self.data['answer_04'] = '12312312'
        response = self.client.post(path='/users/question_create/', data=self.data)
        self.assertFormError(response, 'form', 'right_answer', 'Вы указали blabla как правильный ответ, '
                                                               'но он не совпадает ни с одним из предлагаемых '
                                                               'вариантов ответа на вопрос')


class TestWriteToAdmin(TestUserBase):
    """Testing the user's creation of a message for the admin."""

    def setUp(self):
        """Preparing data for tests."""
        super().setUp()

        self.data = {
            'title': 'Привет',
            'content': 'Пример письма',
            'grade': '5',
        }

    def test_write_to_admin_ok(self):
        """Testing the successful creation of a user message for the admin."""
        response = self.client.post(path='/users/write_to_admin/', data=self.data)
        self.assertRedirects(response, reverse('users:profile'))

    def test_write_to_admin_no_grade(self):
        """Testing the user's unsuccessful creation of a message for the admin: the site is not rated."""
        self.data['grade'] = ''
        response = self.client.post(path='/users/write_to_admin/', data=self.data)
        self.assertFormError(response, 'form', 'grade', 'Обязательное поле.')


class TestTopUsers(TestCase):
    """Testing the view to view the Top 5 participants of the site."""

    def setUp(self):
        """Preparing data for tests."""
        self.client = Client()
        self.test_user_01 = MyUser.objects.create_user(username='test_01',
                                                       first_name='Roland',
                                                       last_name='Emmerich',
                                                       score=35,
                                                       email='blabla@bla.ru')
        self.test_user_01.set_password('laLA12')
        self.test_user_01.is_active = True
        self.test_user_01.save()
        self.client.login(username=self.test_user_01.username, password='laLA12')

        self.test_user_02 = MyUser.objects.create_user(username='test_02',
                                                       first_name='Quentin',
                                                       last_name='Tarantino',
                                                       score=5,
                                                       email='blabla@blabla.ru')
        self.test_user_02.set_password('laLA12')
        self.test_user_02.is_active = True
        self.test_user_02.save()

    def test_top_users_both_are_visible(self):
        """Testing of viewing the Top 5 participants of the site:
        users with the highest total score are visible in the top."""
        response = self.client.get(reverse('users:top_users'))
        self.assertEqual(response.context['top_users'][0], self.test_user_01)
        self.assertEqual(response.context['top_users'][1], self.test_user_02)
        self.assertTemplateUsed('user_activities/top_users.html')

    def test_top_users_one_is_visible(self):
        """Testing of viewing the Top 5 participants of the site: only users with a
        rating greater than 0 are visible in the top."""
        self.test_user_02.score = 0
        self.test_user_02.save()

        response = self.client.get(reverse('users:top_users'))
        self.assertEqual(response.context['top_users'][0], self.test_user_01)
        self.assertEqual(len(response.context['top_users']), 1)
        self.assertFalse(self.test_user_02 in response.context['top_users'])

    def test_top_users_no_one_is_visible(self):
        """Testing the viewing of the Top 5 participants of the site: let the top
        of the site be if all participants have a total score of 0."""
        self.test_user_01.score = 0
        self.test_user_01.save()
        self.test_user_02.score = 0
        self.test_user_02.save()

        response = self.client.get(reverse('users:top_users'))
        self.assertEqual(len(response.context['top_users']), 0)
        self.assertFalse(self.test_user_01 in response.context['top_users'])
        self.assertFalse(self.test_user_02 in response.context['top_users'])
