"""
Contains unit and integration tests for checking the views of the web application.
"""

import logging
import sys

from django.db.models import Q
from django.test import TestCase, Client
from django.urls import reverse

from myadmin.forms import QuestionForm, PostForm, UserAdminRegisterForm, UserAdminProfileForm, CategoryForm
from posts.models import Post
from questions.models import QuestionCategory, Question
from users.models import MyUser

if len(sys.argv) > 1 and sys.argv[1] == 'test':
    logging.disable(logging.CRITICAL)


class TestAdminTwoUsers(TestCase):
    """Parent class with shared settings: creating two test users."""

    def setUp(self):
        """Creating test user objects."""
        self.client = Client()
        self.test_user = MyUser.objects.create_user(username='test_01',
                                                    first_name='Roland',
                                                    last_name='Emmerich',
                                                    email='blabla@bla.ru',
                                                    is_active=True)
        self.test_user.set_password('laLA12')
        self.test_user.is_superuser = True
        self.test_user.save()
        self.test_user_02 = MyUser.objects.create_user(username='PyQT',
                                                       first_name='Quentin',
                                                       last_name='Tarantino',
                                                       email='queenteen@test.ru', )


class TestAdminSeveralUsers(TestCase):
    """Parent class with shared settings: creating several test users."""

    def setUp(self):
        """Creating test user objects."""
        self.client = Client()
        for number in range(1, 8):
            MyUser.objects.create_user(username=f'test_user_{number}',
                                       first_name=f'first_name_{number}',
                                       last_name=f'name_{number}',
                                       email=f'blabla_{number}@bla.ru',
                                       is_active=True)
        self.test_user = MyUser.objects.get(username='test_user_7')
        self.test_user.set_password('laLA12')
        self.test_user.is_superuser = True
        self.test_user.save()


class TestAdminOneUserOneCategory(TestCase):
    """Parent class with shared settings: creating one test user and one test category."""

    def setUp(self):
        """Creating test user and category objects."""
        self.client = Client()

        self.test_category = QuestionCategory.objects.create(name='test_category',
                                                             description='some text')

        self.test_user = MyUser.objects.create_user(username='test_01',
                                                    first_name='Roland',
                                                    last_name='Emmerich',
                                                    email='blabla@bla.ru',
                                                    is_active=True)
        self.test_user.set_password('laLA12')
        self.test_user.is_superuser = True
        self.test_user.save()


class TestAdminOneUserTwoCategories(TestCase):
    """Parent class with shared settings: creating one test user and two test categories."""

    def setUp(self):
        """Creating test user and category objects."""
        self.client = Client()
        self.test_user = MyUser.objects.create_user(username='test_01',
                                                    first_name='Roland',
                                                    last_name='Emmerich',
                                                    email='blabla@bla.ru',
                                                    is_active=True)
        self.test_user.set_password('laLA12')
        self.test_user.is_superuser = True
        self.test_user.save()

        self.test_category_01 = QuestionCategory.objects.create(name='test_category_01',
                                                                description='some text')
        self.test_category_02 = QuestionCategory.objects.create(name='test_category_02',
                                                                description='some text')


class TestAdminOneUserSeveralCategories(TestCase):
    """Parent class with shared settings: creating one test user and several test categories."""

    def setUp(self):
        """Creating test user and categories objects."""
        self.client = Client()
        self.test_user = MyUser.objects.create_user(username='test_01',
                                                    first_name='Roland',
                                                    last_name='Emmerich',
                                                    email='blabla@bla.ru',
                                                    is_active=True)
        self.test_user.set_password('laLA12')
        self.test_user.is_superuser = True
        self.test_user.save()

        for number in range(1, 8):
            QuestionCategory.objects.create(name=f'category_{number}',
                                            description='some text')


class TestAdminPanelView(TestCase):
    """AdminPanelView test."""

    def setUp(self):
        """Creating test user object."""
        self.client = Client()
        self.test_user = MyUser.objects.create_user(username='test_01',
                                                    first_name='Roland',
                                                    last_name='Emmerich',
                                                    email='blabla@bla.ru',
                                                    is_active=True)
        self.test_user.set_password('laLA12')
        self.test_user.is_superuser = True
        self.test_user.save()

    def test_view_authorized_users_only(self):
        """Checks that view and relevant site page are not available to unauthorized users."""
        response = self.client.get('/myadmin/')
        self.assertEqual(response.url, '/users/login/?next=/myadmin/')
        self.assertEqual(response.status_code, 302)

    def test_view_superusers_only(self):
        """Checks that AdminPanelView view and relevant site page are only available to superusers"""
        self.test_user.is_superuser = False
        self.test_user.save()
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/myadmin/')
        self.assertEqual(response.url, '/users/login/?next=/myadmin/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_exists_at_desired_location(self):
        """Checks that the view URL exists in the desired location"""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/myadmin/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Checks if the view URL is available by name"""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_index'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template_and_title(self):
        """Checks that the view uses the correct template and title"""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myadmin/admin.html')
        self.assertEqual(response.context['title'], 'Админка')


class TestAdminUserListView(TestAdminSeveralUsers):
    """UserListView test."""

    def test_view_authorized_users_only(self):
        """Checks that view and relevant site page are not available to unauthorized users."""
        response = self.client.get('/myadmin/users/')
        self.assertEqual(response.url, '/users/login/?next=/myadmin/users/')
        self.assertEqual(response.status_code, 302)

    def test_view_superusers_only(self):
        """Checks that UserListView view and relevant site page are only available to superusers."""
        self.test_user.is_superuser = False
        self.test_user.save()
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/myadmin/users/')
        self.assertEqual(response.url, '/users/login/?next=/myadmin/users/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_exists_at_desired_location(self):
        """Checks that the view URL exists in the desired location."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/myadmin/users/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Checks if the view URL is available by name."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_users'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template_and_title(self):
        """Checks that the view uses the correct template and title."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_users'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myadmin/users/users-viewing.html')
        self.assertEqual(response.context['title'], 'Просмотр пользователей')

    def test_view_uses_pagination_page_2(self):
        """Checks that pagination is used and 3 objects are displayed on the page, the second page is used."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_users') + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertTrue(len(response.context['users']) == 3)

    def test_view_uses_context_object_name(self):
        """Checks that the specified context object name is used."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_users') + '?page=2')
        self.assertTrue('users' in response.context)


class TestAdminUserCreateView(TestCase):
    """UserCreateView test."""

    def setUp(self):
        """Creating test user object."""
        self.client = Client()
        self.test_user = MyUser.objects.create_user(username='test_01',
                                                    first_name='Roland',
                                                    last_name='Emmerich',
                                                    email='blabla@bla.ru',
                                                    is_active=True)
        self.test_user.set_password('laLA12')
        self.test_user.is_superuser = True
        self.test_user.save()

    def test_view_authorized_users_only(self):
        """Checks that view and relevant site page are not available to unauthorized users."""
        response = self.client.get('/myadmin/users-create/')
        self.assertEqual(response.url, '/users/login/?next=/myadmin/users-create/')
        self.assertEqual(response.status_code, 302)

    def test_view_superusers_only(self):
        """Checks that UserCreateView view and relevant site page are only available to superusers."""
        self.test_user.is_superuser = False
        self.test_user.save()
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/myadmin/users-create/')
        self.assertEqual(response.url, '/users/login/?next=/myadmin/users-create/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_exists_at_desired_location(self):
        """Checks that the view URL exists in the desired location."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/myadmin/users-create/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Checks if the view URL is available by name."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_user_create'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template_and_title(self):
        """Checks that the view uses the correct template and title."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_user_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myadmin/users/users-creating.html')
        self.assertEqual(response.context['title'], 'Добавить пользователя')

    def test_view_uses_correct_form_class(self):
        """Checks that the view uses the correct form class."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_user_create'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], UserAdminRegisterForm)


class TestAdminUserUpdateView(TestAdminTwoUsers):
    """UserUpdateView test."""

    def test_view_authorized_users_only(self):
        """Checks that view and relevant site page are not available to unauthorized users."""
        response = self.client.get(f'/myadmin/users-update/{self.test_user_02.id}/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/users/login/?next=/myadmin/users-update/{self.test_user_02.id}/')

    def test_view_superusers_only(self):
        """Checks that UserUpdateView view and relevant site page are only available to superusers."""
        self.test_user.is_superuser = False
        self.test_user.save()
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(f'/myadmin/users-update/{self.test_user_02.id}/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/users/login/?next=/myadmin/users-update/{self.test_user_02.id}/')

    def test_view_url_exists_at_desired_location(self):
        """Checks that the view URL exists in the desired location."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(f'/myadmin/users-update/{self.test_user_02.id}/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Checks if the view URL is available by name."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_user_update', args=[self.test_user_02.id]))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template_and_title(self):
        """Checks that the view uses the correct template and title."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_user_update', args=[self.test_user_02.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myadmin/users/users-update.html')
        self.assertEqual(response.context['title'], 'Изменить пользователя')

    def test_view_uses_correct_form_class(self):
        """Checks that the view uses the correct form class."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_user_update', args=[self.test_user_02.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], UserAdminProfileForm)


class TestAdminUserDeleteView(TestAdminTwoUsers):
    """UserDeleteView test."""

    def test_view_authorized_users_only(self):
        """Checks that view and relevant site page are not available to unauthorized users."""
        response = self.client.get(f'/myadmin/users-delete/{self.test_user_02.id}/')
        self.assertEqual(response.url, f'/users/login/?next=/myadmin/users-delete/{self.test_user_02.id}/')
        self.assertEqual(response.status_code, 302)

    def test_view_superusers_only(self):
        """Checks that UserDeleteView view and relevant site page are only available to superusers."""
        url = f'/myadmin/users-delete/{self.test_user_02.id}/'
        self.test_user.is_superuser = False
        self.test_user.save()
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(url)
        self.assertEqual(response.url, f'/users/login/?next=/myadmin/users-delete/{self.test_user_02.id}/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_exists_at_desired_location(self):
        """Checks that the view URL exists in the desired location."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(f'/myadmin/users-delete/{self.test_user_02.id}/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Checks if the view URL is available by name."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_user_delete', args=[self.test_user_02.id]))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Checks that the view uses the correct template and title."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_user_delete', args=[self.test_user_02.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myadmin/users/users-update.html')

    def test_view_activate_user(self):
        """Checks the activation of a specific user."""
        user = MyUser.objects.get(id=self.test_user_02.id)
        self.assertFalse(user.is_active)

        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.post(reverse('myadmin:admins_user_delete', args=[self.test_user_02.id]),
                                    {'flag': ['false'], })
        self.assertEqual(response.status_code, 200)
        user = MyUser.objects.get(id=self.test_user_02.id)
        self.assertTrue(user.is_active)

    def test_view_delete_user(self):
        """Checks the deletion of a specific user."""
        user = MyUser.objects.get(id=self.test_user_02.id)
        self.assertFalse(user.is_active)

        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.post(reverse('myadmin:admins_user_delete', args=[self.test_user_02.id]),
                                    {'flag': ['true'], })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(MyUser.objects.filter(id=self.test_user_02.id).exists())


class TestAdminUserIsStaff(TestAdminTwoUsers):
    """UserIsStaff test."""

    def test_view_authorized_users_only(self):
        """Checks that view and relevant site page are not available to unauthorized users."""
        response = self.client.get(f'/myadmin/users-is-staff/{self.test_user_02.id}/')
        self.assertEqual(response.url, f'/users/login/?next=/myadmin/users-is-staff/{self.test_user_02.id}/')
        self.assertEqual(response.status_code, 302)

    def test_view_superusers_only(self):
        """Checks that UserIsStaff view and relevant site page are only available to superusers."""
        self.test_user.is_superuser = False
        self.test_user.save()
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(f'/myadmin/users-is-staff/{self.test_user_02.id}/')
        self.assertEqual(response.url, f'/users/login/?next=/myadmin/users-is-staff/{self.test_user_02.id}/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_exists_at_desired_location(self):
        """Checks that the view URL exists in the desired location."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(f'/myadmin/users-is-staff/{self.test_user_02.id}/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Checks if the view URL is available by name."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_user_is_staff', args=[self.test_user_02.id]))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Checks that the view uses the correct template and title."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_user_is_staff', args=[self.test_user_02.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myadmin/includes/table-users.html')

    def test_view_set_user_stuff_rights(self):
        """Test of granting the user the rights of a superuser."""
        user = MyUser.objects.get(id=self.test_user_02.id)
        self.assertFalse(user.is_staff)
        self.client.login(username=self.test_user.username, password='laLA12')

        response = self.client.post(reverse('myadmin:admins_user_is_staff', args=[self.test_user_02.id]),
                                    {'elements': [self.test_user.id, self.test_user_02.id], })
        self.assertEqual(response.status_code, 200)
        user = MyUser.objects.get(id=self.test_user_02.id)
        self.assertTrue(user.is_staff)

    def test_view_removing_user_stuff_rights(self):
        """Test of removing superuser rights from a user."""
        user = MyUser.objects.get(id=self.test_user_02.id)
        user.is_staff = True
        user.save()
        self.assertTrue(user.is_staff)
        self.client.login(username=self.test_user.username, password='laLA12')

        response = self.client.post(reverse('myadmin:admins_user_is_staff', args=[self.test_user_02.id]),
                                    {'elements': [self.test_user.id, self.test_user_02.id], })
        self.assertEqual(response.status_code, 200)
        user = MyUser.objects.get(id=self.test_user_02.id)
        self.assertFalse(user.is_staff)


class TestAdminCategoriesListView(TestAdminOneUserSeveralCategories):
    """CategoriesListView test."""

    def test_view_authorized_users_only(self):
        """Checks that view and relevant site page are not available to unauthorized users."""
        response = self.client.get('/myadmin/categories/')
        self.assertEqual(response.url, '/users/login/?next=/myadmin/categories/')
        self.assertEqual(response.status_code, 302)

    def test_view_superusers_only(self):
        """Checks that CategoriesListView view and relevant site page are only available to superusers."""
        self.test_user.is_superuser = False
        self.test_user.save()
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/myadmin/categories/')
        self.assertEqual(response.url, '/users/login/?next=/myadmin/categories/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_exists_at_desired_location(self):
        """Checks that the view URL exists in the desired location."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/myadmin/categories/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Checks if the view URL is available by name."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_categories'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template_and_title(self):
        """Checks that the view uses the correct template and title."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_categories'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myadmin/categories/category-viewing.html')
        self.assertEqual(response.context['title'], 'Просмотр категорий')

    def test_view_uses_pagination_page_2(self):
        """Checks that pagination is used and 2 objects are displayed on the page, the second page is used."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_categories') + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertTrue(len(response.context['categories']) == 2)

    def test_view_uses_context_object_name(self):
        """Checks that the specified context object name is used."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_categories') + '?page=2')
        self.assertTrue('categories' in response.context)


class TestAdminCategoriesCreateView(TestCase):
    """CategoriesCreateView test."""

    def setUp(self):
        """Creating test user object."""
        self.client = Client()
        self.test_user = MyUser.objects.create_user(username='test_01',
                                                    first_name='Roland',
                                                    last_name='Emmerich',
                                                    email='blabla@bla.ru',
                                                    is_active=True)
        self.test_user.set_password('laLA12')
        self.test_user.is_superuser = True
        self.test_user.save()

    def test_view_authorized_users_only(self):
        """Checks that view and relevant site page are not available to unauthorized users."""
        response = self.client.get('/myadmin/categories-create/')
        self.assertEqual(response.url, '/users/login/?next=/myadmin/categories-create/')
        self.assertEqual(response.status_code, 302)

    def test_view_superusers_only(self):
        """Checks that CategoriesCreateView view and relevant site page are only available to superusers."""
        self.test_user.is_superuser = False
        self.test_user.save()
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/myadmin/categories-create/')
        self.assertEqual(response.url, '/users/login/?next=/myadmin/categories-create/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_exists_at_desired_location(self):
        """Checks that the view URL exists in the desired location."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/myadmin/categories-create/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Checks if the view URL is available by name."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_category_create'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template_and_title(self):
        """Checks that the view uses the correct template and title."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_category_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myadmin/categories/category-creating.html')
        self.assertEqual(response.context['title'], 'Добавить категорию')

    def test_view_uses_correct_form_class(self):
        """Checks that the view uses the correct form class."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_category_create'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], CategoryForm)


class TestAdminCategoriesUpdateView(TestAdminOneUserOneCategory):
    """CategoriesUpdateView test."""

    def test_view_authorized_users_only(self):
        """Checks that view and relevant site page are not available to unauthorized users."""
        response = self.client.get(f'/myadmin/categories-update/{self.test_category.id}/')
        self.assertEqual(response.url, f'/users/login/?next=/myadmin/categories-update/{self.test_category.id}/')
        self.assertEqual(response.status_code, 302)

    def test_view_superusers_only(self):
        """Checks that CategoriesUpdateView view and relevant site page are only available to superusers."""
        self.test_user.is_superuser = False
        self.test_user.save()
        self.client.login(username=self.test_user.username, password='laLA12')
        url = f'/myadmin/categories-update/{self.test_category.id}/'
        response = self.client.get(url)
        self.assertEqual(response.url, f'/users/login/?next=/myadmin/categories-update/{self.test_category.id}/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_exists_at_desired_location(self):
        """Checks that the view URL exists in the desired location."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(f'/myadmin/categories-update/{self.test_category.id}/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Checks if the view URL is available by name."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_category_update', args=[self.test_category.id]))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template_and_title(self):
        """Checks that the view uses the correct template and title."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_category_update', args=[self.test_category.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myadmin/categories/category-update.html')
        self.assertEqual(response.context['title'], 'Изменить категорию')

    def test_view_uses_correct_form_class(self):
        """Checks that the view uses the correct form class."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_category_update', args=[self.test_category.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], CategoryForm)


class TestAdminCategoriesDeleteView(TestAdminOneUserOneCategory):
    """CategoriesDeleteView test."""

    def test_view_authorized_users_only(self):
        """Checks that view and relevant site page are not available to unauthorized users."""
        response = self.client.get(f'/myadmin/categories-delete/{self.test_category.id}/')
        self.assertEqual(response.url, f'/users/login/?next=/myadmin/categories-delete/{self.test_category.id}/')
        self.assertEqual(response.status_code, 302)

    def test_view_superusers_only(self):
        """Checks that CategoriesDeleteView view and relevant site page are only available to superusers."""
        self.test_user.is_superuser = False
        self.test_user.save()
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(f'/myadmin/categories-delete/{self.test_category.id}/')
        self.assertEqual(response.url, f'/users/login/?next=/myadmin/categories-delete/{self.test_category.id}/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_exists_at_desired_location(self):
        """Checks that the view URL exists in the desired location."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(f'/myadmin/categories-delete/{self.test_category.id}/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Checks if the view URL is available by name."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_category_delete', args=[self.test_category.id]))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Checks that the view uses the correct template and title."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_category_delete', args=[self.test_category.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myadmin/categories/category-update.html')

    def test_view_deactivate_category(self):
        """Checks the activation of a specific category."""
        category = QuestionCategory.objects.get(id=self.test_category.id)
        self.assertTrue(category.available)

        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.post(reverse('myadmin:admins_category_delete', args=[self.test_category.id]),
                                    {'flag': ['false'], })
        self.assertEqual(response.status_code, 200)
        category = QuestionCategory.objects.get(id=self.test_category.id)
        self.assertFalse(category.available)

    def test_view_delete_category(self):
        """Checks the deletion of a specific category."""
        category = QuestionCategory.objects.get(id=self.test_category.id)
        self.assertTrue(category.available)

        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.post(reverse('myadmin:admins_category_delete', args=[self.test_category.id]),
                                    {'flag': ['true'], })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(QuestionCategory.objects.filter(id=self.test_category.id).exists())


class TestAdminQuestionListView(TestAdminOneUserTwoCategories):
    """QuestionListView test."""

    def setUp(self):
        """Creating test user, questions and categories objects."""
        super().setUp()
        for number in range(1, 8):
            question = Question.objects.create(question=f'question_{number}',
                                               subject=self.test_category_01,
                                               author=self.test_user,
                                               right_answer='right_answer',
                                               answer_01='right_answer',
                                               answer_02='wrong_answer',
                                               answer_03='wrong_answer',
                                               answer_04='wrong_answer',
                                               available=True)
            if number % 2 == 0:
                question.subject = self.test_category_02
                question.save()

    def test_view_authorized_users_only(self):
        """Checks that view and relevant site page are not available to unauthorized users."""
        response = self.client.get('/myadmin/questions/')
        self.assertEqual(response.url, '/users/login/?next=/myadmin/questions/')
        self.assertEqual(response.status_code, 302)

    def test_view_superusers_only(self):
        """Checks that QuestionListView view and relevant site page are only available to superusers."""
        self.test_user.is_superuser = False
        self.test_user.save()
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/myadmin/questions/')
        self.assertEqual(response.url, '/users/login/?next=/myadmin/questions/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_exists_at_desired_location(self):
        """Checks that the view URL exists in the desired location."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/myadmin/questions/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Checks if the view URL is available by name."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_questions'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template_and_title(self):
        """Checks that the view uses the correct template and title."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_questions'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myadmin/questions/question-viewing.html')
        self.assertEqual(response.context['title'], 'Просмотр вопросов')

    def test_view_uses_pagination_page_2(self):
        """Checks that pagination is used and 3 objects are displayed on the page, the second page is used."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_questions') + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertTrue(len(response.context['questions']) == 3)

    def test_view_uses_context_object_name(self):
        """Checks that the specified context object name is used."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_questions') + '?page=2')
        self.assertTrue('questions' in response.context)

    def test_view_filter_queryset(self):
        """Checks the filtering of queryset questions according to the category value
        set by the user and the placement of the filter value in the session.
        Also checks the removal of the filter from the session and the return of
        the correct queryset when the user removes the filter."""
        self.client.login(username=self.test_user.username, password='laLA12')

        response = self.client.get(reverse('myadmin:admins_questions'),
                                   {'filter': [self.test_category_01.id]})
        for item in response.context['questions']:
            self.assertTrue(item.subject == self.test_category_01)
        self.assertTrue(self.client.session['filter'] == '1')
        self.assertTrue(len(response.context['questions']) == 3)

        response = self.client.get(reverse('myadmin:admins_questions'),
                                   {'filter': [self.test_category_02.id]})
        for item in response.context['questions']:
            self.assertTrue(item.subject == self.test_category_02)
        self.assertTrue(self.client.session['filter'] == '2')
        self.assertTrue(len(response.context['questions']) == 3)

        response = self.client.get(reverse('myadmin:admins_questions'),
                                   {'filter': 'all'})
        questions = Question.objects.all()[:3]
        self.assertQuerysetEqual(response.context['questions'], questions, ordered=False)
        self.assertIsNone(self.client.session['filter'])
        self.assertTrue(len(response.context['questions']) == 3)


class TestAdminQuestionCreateView(TestAdminOneUserOneCategory):
    """QuestionCreateView test."""

    def test_view_authorized_users_only(self):
        """Checks that view and relevant site page are not available to unauthorized users."""
        response = self.client.get('/myadmin/questions-create/')
        self.assertEqual(response.url, '/users/login/?next=/myadmin/questions-create/')
        self.assertEqual(response.status_code, 302)

    def test_view_superusers_only(self):
        """Checks that QuestionCreateView view and relevant site page are only available to superusers."""
        self.test_user.is_superuser = False
        self.test_user.save()
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/myadmin/questions-create/')
        self.assertEqual(response.url, '/users/login/?next=/myadmin/questions-create/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_exists_at_desired_location(self):
        """Checks that the view URL exists in the desired location."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/myadmin/questions-create/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Checks if the view URL is available by name."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_question_create'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template_and_title(self):
        """Checks that the view uses the correct template and title."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_question_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myadmin/questions/question-creating.html')
        self.assertEqual(response.context['title'], 'Добавить вопрос')

    def test_view_uses_correct_form_class(self):
        """Checks that the view uses the correct form class."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_question_create'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], QuestionForm)

    def test_post_new_question_create(self):
        """Checks the creation of a new question with automatic assignment
        of the author after the user sends the data.
        """
        form_data = {
            'question': 'В чем сила, брат?',
            'subject': self.test_category.id,
            'right_answer': 'Сила в правде',
            'answer_01': 'Сила в деньгах',
            'answer_02': 'Сила во власти',
            'answer_03': 'Сила в правде',
            'answer_04': 'Сила в свободе',
            'difficulty_level': 'NB',
            'tag': 'Классика',
            'available': False,
        }
        self.client.login(username=self.test_user.username, password='laLA12')
        self.client.post(reverse('myadmin:admins_question_create'), form_data)
        self.assertTrue(Question.objects.filter(question='В чем сила, брат?').exists())
        self.assertTrue(len(Question.objects.filter(question='В чем сила, брат?')) == 1)


class TestAdminQuestionUpdateView(TestCase):
    """QuestionUpdateView test."""

    def setUp(self):
        """Creating test user, question and category objects."""
        self.client = Client()
        self.test_user = MyUser.objects.create_user(username='test_01',
                                                    first_name='Roland',
                                                    last_name='Emmerich',
                                                    email='blabla@bla.ru',
                                                    is_active=True)
        self.test_user.set_password('laLA12')
        self.test_user.is_superuser = True
        self.test_user.save()

        self.test_category = QuestionCategory.objects.create(name='test_category',
                                                             description='some text')
        self.test_question = Question.objects.create(question=f'question',
                                                     subject=self.test_category,
                                                     author=self.test_user,
                                                     right_answer='right_answer',
                                                     answer_01='right_answer',
                                                     answer_02='wrong_answer',
                                                     answer_03='wrong_answer',
                                                     answer_04='wrong_answer',
                                                     available=True)

    def test_view_authorized_users_only(self):
        """Checks that view and relevant site page are not available to unauthorized users."""
        response = self.client.get(f'/myadmin/questions-update/{self.test_question.id}/')
        self.assertEqual(response.url, f'/users/login/?next=/myadmin/questions-update/{self.test_question.id}/')
        self.assertEqual(response.status_code, 302)

    def test_view_superusers_only(self):
        """Checks that QuestionUpdateView view and relevant site page are only available to superusers."""
        self.test_user.is_superuser = False
        self.test_user.save()
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(f'/myadmin/questions-update/{self.test_question.id}/')
        self.assertEqual(response.url, f'/users/login/?next=/myadmin/questions-update/{self.test_question.id}/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_exists_at_desired_location(self):
        """Checks that the view URL exists in the desired location."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(f'/myadmin/questions-update/{self.test_question.id}/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Checks if the view URL is available by name."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_question_update', args=[self.test_question.id]))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template_and_title(self):
        """Checks that the view uses the correct template and title."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_question_update', args=[self.test_question.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myadmin/questions/question-update.html')
        self.assertEqual(response.context['title'], 'Изменить вопрос')

    def test_view_uses_correct_form_class(self):
        """Checks that the view uses the correct form class."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_question_update', args=[self.test_question.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], QuestionForm)


class TestAdminQuestionDeleteView(TestAdminOneUserOneCategory):
    """QuestionDeleteView test."""

    def setUp(self):
        """Creating test user, question and category objects."""
        super().setUp()
        self.test_question = Question.objects.create(question='question',
                                                     subject=self.test_category,
                                                     author=self.test_user,
                                                     right_answer='right_answer',
                                                     answer_01='right_answer',
                                                     answer_02='wrong_answer',
                                                     answer_03='wrong_answer',
                                                     answer_04='wrong_answer',
                                                     available=True)

    def test_view_authorized_users_only(self):
        """Checks that view and relevant site page are not available to unauthorized users."""
        response = self.client.get(f'/myadmin/questions-delete/{self.test_question.id}/')
        self.assertEqual(response.url, f'/users/login/?next=/myadmin/questions-delete/{self.test_question.id}/')
        self.assertEqual(response.status_code, 302)

    def test_view_superusers_only(self):
        """Checks that QuestionDeleteView view and relevant site page are only available to superusers."""
        self.test_user.is_superuser = False
        self.test_user.save()
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(f'/myadmin/questions-delete/{self.test_question.id}/')
        self.assertEqual(response.url, f'/users/login/?next=/myadmin/questions-delete/{self.test_question.id}/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_exists_at_desired_location(self):
        """Checks that the view URL exists in the desired location."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(f'/myadmin/questions-delete/{self.test_question.id}/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Checks if the view URL is available by name."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_question_delete', args=[self.test_question.id]))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Checks that the view uses the correct template and title."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_question_delete', args=[self.test_question.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myadmin/questions/question-update.html')

    def test_view_deactivate_question(self):
        """Checks the activation of a specific question."""
        question = Question.objects.get(id=self.test_question.id)
        self.assertTrue(question.available)

        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.post(reverse('myadmin:admins_question_delete', args=[self.test_question.id]),
                                    {'flag': ['false'], })
        self.assertEqual(response.status_code, 200)
        question = Question.objects.get(id=self.test_question.id)
        self.assertFalse(question.available)

    def test_view_delete_question(self):
        """Checks the deletion of a specific question."""
        question = Question.objects.get(id=self.test_question.id)
        self.assertTrue(question.available)

        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.post(reverse('myadmin:admins_question_delete', args=[self.test_question.id]),
                                    {'flag': ['true'], })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Question.objects.filter(id=self.test_question.id).exists())


class TestAdminPostListView(TestAdminOneUserTwoCategories):
    """PostListView test."""

    def setUp(self):
        """Creating test user, posts and categories objects."""
        super().setUp()

        for number in range(1, 8):
            post = Post.objects.create(title=f'post_{number}',
                                       author=self.test_user,
                                       category=self.test_category_01,
                                       body='some text',
                                       available=True)
            if number % 2 == 0:
                post.category = self.test_category_02
                post.save()

    def test_view_authorized_users_only(self):
        """Checks that view and relevant site page are not available to unauthorized users."""
        response = self.client.get('/myadmin/posts/')
        self.assertEqual(response.url, '/users/login/?next=/myadmin/posts/')
        self.assertEqual(response.status_code, 302)

    def test_view_superusers_only(self):
        """Checks that PostListView view and relevant site page are only available to superusers."""
        self.test_user.is_superuser = False
        self.test_user.save()
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/myadmin/posts/')
        self.assertEqual(response.url, '/users/login/?next=/myadmin/posts/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_exists_at_desired_location(self):
        """Checks that the view URL exists in the desired location."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/myadmin/posts/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Checks if the view URL is available by name."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_posts'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template_and_title(self):
        """Checks that the view uses the correct template and title."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_posts'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myadmin/posts/post-viewing.html')
        self.assertEqual(response.context['title'], 'Просмотр статей')

    def test_view_uses_pagination_page_2(self):
        """Checks that pagination is used and 3 objects are displayed on the page, the second page is used."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_posts') + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertTrue(len(response.context['posts']) == 3)

    def test_view_uses_context_object_name(self):
        """Checks that the specified context object name is used."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_posts') + '?page=2')
        self.assertTrue('posts' in response.context)

    def test_view_filter_queryset(self):
        """Checks the filtering of queryset posts according to the category value
        set by the user and the placement of the filter value in the session.
        Also checks the removal of the filter from the session and the return of
        the correct queryset when the user removes the filter.
        """
        self.client.login(username=self.test_user.username, password='laLA12')

        response = self.client.get(reverse('myadmin:admins_posts'),
                                   {'filter': [self.test_category_01.id]})
        for item in response.context['posts']:
            self.assertTrue(item.category == self.test_category_01)
        self.assertTrue(self.client.session['filter'] == '1')
        self.assertTrue(len(response.context['posts']) == 3)

        response = self.client.get(reverse('myadmin:admins_posts'),
                                   {'filter': [self.test_category_02.id]})
        for item in response.context['posts']:
            self.assertTrue(item.category == self.test_category_02)
        self.assertTrue(self.client.session['filter'] == '2')
        self.assertTrue(len(response.context['posts']) == 3)

        response = self.client.get(reverse('myadmin:admins_posts'),
                                   {'filter': 'all'})
        posts = Post.objects.all()[:3]
        self.assertQuerysetEqual(response.context['posts'], posts, ordered=False)
        self.assertIsNone(self.client.session['filter'])
        self.assertTrue(len(response.context['posts']) == 3)


class TestAdminPostCreateView(TestAdminOneUserOneCategory):
    """PostCreateView test."""

    def test_view_authorized_users_only(self):
        """Checks that view and relevant site page are not available to unauthorized users."""
        response = self.client.get('/myadmin/posts-create/')
        self.assertEqual(response.url, '/users/login/?next=/myadmin/posts-create/')
        self.assertEqual(response.status_code, 302)

    def test_view_superusers_only(self):
        """Checks that PostCreateView view and relevant site page are only available to superusers."""
        self.test_user.is_superuser = False
        self.test_user.save()
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/myadmin/posts-create/')
        self.assertEqual(response.url, '/users/login/?next=/myadmin/posts-create/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_exists_at_desired_location(self):
        """Checks that the view URL exists in the desired location."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/myadmin/posts-create/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Checks if the view URL is available by name."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_post_create'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template_and_title(self):
        """Checks that the view uses the correct template and title."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_post_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myadmin/posts/post-creating.html')
        self.assertEqual(response.context['title'], 'Добавить статью')

    def test_view_uses_correct_form_class(self):
        """Checks that the view uses the correct form class."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_post_create'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], PostForm)

    def test_post_new_post_create(self):
        """Checks the creation of a new post with automatic assignment
        of the author after the user sends the data.
        """
        form_data = {
            'title': 'В чем сила, брат?',
            'category': self.test_category.id,
            'body': 'Сила в правде',
            'tag': 'Классика',
            'available': False,
        }
        self.client.login(username=self.test_user.username, password='laLA12')
        self.client.post(reverse('myadmin:admins_post_create'), form_data)
        self.assertTrue(Post.objects.filter(title='В чем сила, брат?').exists())
        self.assertTrue(len(Post.objects.filter(title='В чем сила, брат?')) == 1)


class TestAdminPostUpdateView(TestAdminOneUserOneCategory):
    """PostUpdateView test."""

    def setUp(self):
        """Creating test user, post and category objects."""
        super().setUp()
        self.test_post = Post.objects.create(title='post',
                                             category=self.test_category,
                                             author=self.test_user,
                                             body='right_answer',
                                             available=True)

    def test_view_authorized_users_only(self):
        """Checks that view and relevant site page are not available to unauthorized users."""
        response = self.client.get(f'/myadmin/posts-update/{self.test_post.id}/')
        self.assertEqual(response.url, f'/users/login/?next=/myadmin/posts-update/{self.test_post.id}/')
        self.assertEqual(response.status_code, 302)

    def test_view_superusers_only(self):
        """Checks that PostUpdateView view and relevant site page are only available to superusers."""
        self.test_user.is_superuser = False
        self.test_user.save()
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(f'/myadmin/posts-update/{self.test_post.id}/')
        self.assertEqual(response.url, f'/users/login/?next=/myadmin/posts-update/{self.test_post.id}/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_exists_at_desired_location(self):
        """Checks that the view URL exists in the desired location."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(f'/myadmin/posts-update/{self.test_post.id}/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Checks if the view URL is available by name."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_post_update', args=[self.test_post.id]))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template_and_title(self):
        """Checks that the view uses the correct template and title."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_post_update', args=[self.test_post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myadmin/posts/post-update.html')
        self.assertEqual(response.context['title'], 'Изменить статью')

    def test_view_uses_correct_form_class(self):
        """Checks that the view uses the correct form class."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_post_update', args=[self.test_post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], PostForm)


class TestAdminPostDeleteView(TestAdminOneUserOneCategory):
    """PostDeleteView test."""

    def setUp(self):
        """Creating test user, post and category objects."""
        super().setUp()
        self.test_post = Post.objects.create(title='post',
                                             category=self.test_category,
                                             author=self.test_user,
                                             body='right_answer',
                                             available=True)

    def test_view_authorized_users_only(self):
        """Checks that view and relevant site page are not available to unauthorized users."""
        response = self.client.get(f'/myadmin/posts-delete/{self.test_post.id}/')
        self.assertEqual(response.url, f'/users/login/?next=/myadmin/posts-delete/{self.test_post.id}/')
        self.assertEqual(response.status_code, 302)

    def test_view_superusers_only(self):
        """Checks that PostDeleteView view and relevant site page are only available to superusers."""
        self.test_user.is_superuser = False
        self.test_user.save()
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(f'/myadmin/posts-delete/{self.test_post.id}/')
        self.assertEqual(response.url, f'/users/login/?next=/myadmin/posts-delete/{self.test_post.id}/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_exists_at_desired_location(self):
        """Checks that the view URL exists in the desired location."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(f'/myadmin/posts-delete/{self.test_post.id}/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Checks if the view URL is available by name."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_post_delete', args=[self.test_post.id]))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Checks that the view uses the correct template and title."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_post_delete', args=[self.test_post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myadmin/posts/post-update.html')

    def test_view_deactivate_post(self):
        """Checks the activation of a specific post."""
        post = Post.objects.get(id=self.test_post.id)
        self.assertTrue(post.available)

        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.post(reverse('myadmin:admins_post_delete', args=[self.test_post.id]),
                                    {'flag': ['false'], })
        self.assertEqual(response.status_code, 200)
        post = Post.objects.get(id=self.test_post.id)
        self.assertFalse(post.available)

    def test_view_delete_post(self):
        """Checks the deletion of a specific post."""
        post = Post.objects.get(id=self.test_post.id)
        self.assertTrue(post.available)

        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.post(reverse('myadmin:admins_post_delete', args=[self.test_post.id]),
                                    {'flag': ['true'], })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Post.objects.filter(id=self.test_post.id).exists())


class TestAdminsSearchUserView(TestAdminSeveralUsers):
    """AdminsSearchUserView test."""

    def test_view_authorized_users_only(self):
        """Checks that view and relevant site page are not available to unauthorized users."""
        response = self.client.get('/myadmin/search/user/')
        self.assertEqual(response.url, '/users/login/?next=/myadmin/search/user/')
        self.assertEqual(response.status_code, 302)

    def test_view_superusers_only(self):
        """Checks that AdminsSearchUserView view and relevant site page are only available to superusers."""
        self.test_user.is_superuser = False
        self.test_user.save()
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/myadmin/search/user/')
        self.assertEqual(response.url, '/users/login/?next=/myadmin/search/user/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_exists_at_desired_location(self):
        """Checks that the view URL exists in the desired location."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/myadmin/search/user/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Checks if the view URL is available by name."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_search_results_user'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template_and_title(self):
        """Checks that the view uses the correct template and title."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_search_results_user'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myadmin/users/search_results_user.html')
        self.assertEqual(response.context['title'], 'Поиск пользователя')

    def test_view_returns_correctly_filtered_queryset(self):
        """Checks that view returns a correctly filtered queryset."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_search_results_user'),
                                   {'admins_search_panel': 'first_name'})

        users = MyUser.objects.filter(Q(username__icontains='first_name') |
                                      Q(last_name__icontains='first_name') |
                                      Q(first_name__contains='first_name'))
        self.assertQuerysetEqual(response.context['object_list'], users, ordered=False)

        response = self.client.get(reverse('myadmin:admins_search_results_user'),
                                   {'admins_search_panel': '6'})

        users = MyUser.objects.filter(Q(username__icontains='6') |
                                      Q(last_name__icontains='6') |
                                      Q(first_name__contains='6'))
        self.assertQuerysetEqual(response.context['object_list'], users, ordered=False)


class TestAdminsSearchCategoryView(TestAdminOneUserSeveralCategories):
    """AdminsSearchCategoryView test."""

    def test_view_authorized_users_only(self):
        """Checks that view and relevant site page are not available to unauthorized users."""
        response = self.client.get('/myadmin/search/cat/')
        self.assertEqual(response.url, '/users/login/?next=/myadmin/search/cat/')
        self.assertEqual(response.status_code, 302)

    def test_view_superusers_only(self):
        """Checks that AdminsSearchCategoryView view and relevant site page are only available to superusers."""
        self.test_user.is_superuser = False
        self.test_user.save()
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/myadmin/search/cat/')
        self.assertEqual(response.url, '/users/login/?next=/myadmin/search/cat/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_exists_at_desired_location(self):
        """Checks that the view URL exists in the desired location."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/myadmin/search/cat/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Checks if the view URL is available by name."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_search_results_category'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template_and_title(self):
        """Checks that the view uses the correct template and title."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_search_results_category'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myadmin/categories/search_results_category.html')
        self.assertEqual(response.context['title'], 'Поиск категории')

    def test_view_returns_correctly_filtered_queryset(self):
        """Checks that view returns a correctly filtered queryset."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_search_results_category'),
                                   {'admins_search_panel': 'category'})

        categories = QuestionCategory.objects.filter(name__icontains='category')
        self.assertQuerysetEqual(response.context['object_list'], categories, ordered=False)

        response = self.client.get(reverse('myadmin:admins_search_results_category'),
                                   {'admins_search_panel': '6'})

        categories = QuestionCategory.objects.filter(name__icontains='6')
        self.assertQuerysetEqual(response.context['object_list'], categories, ordered=False)


class TestAdminsSearchQuestionView(TestAdminOneUserOneCategory):
    """AdminsSearchQuestionView test."""

    def setUp(self):
        """Creating test user, question and category objects."""
        super().setUp()

        for number in range(1, 8):
            Question.objects.create(question=f'question_{number}',
                                    subject=self.test_category,
                                    author=self.test_user,
                                    right_answer='right_answer',
                                    answer_01='right_answer',
                                    answer_02='wrong_answer',
                                    answer_03='wrong_answer',
                                    answer_04='wrong_answer',
                                    available=True)

    def test_view_authorized_users_only(self):
        """Checks that view and relevant site page are not available to unauthorized users."""
        response = self.client.get('/myadmin/search/question/')
        self.assertEqual(response.url, '/users/login/?next=/myadmin/search/question/')
        self.assertEqual(response.status_code, 302)

    def test_view_superusers_only(self):
        """Checks that AdminsSearchQuestionView view and relevant site page are only available to superusers."""
        self.test_user.is_superuser = False
        self.test_user.save()
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/myadmin/search/question/')
        self.assertEqual(response.url, '/users/login/?next=/myadmin/search/question/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_exists_at_desired_location(self):
        """Checks that the view URL exists in the desired location."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/myadmin/search/question/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Checks if the view URL is available by name."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_search_results_question'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template_and_title(self):
        """Checks that the view uses the correct template and title."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_search_results_question'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myadmin/questions/search_results_question.html')
        self.assertEqual(response.context['title'], 'Поиск вопроса')

    def test_view_returns_correctly_filtered_queryset(self):
        """Checks that view returns a correctly filtered queryset."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_search_results_question'),
                                   {'admins_search_panel': 'question'})

        questions = Question.objects.filter(Q(question__icontains='question') | Q(tag__icontains='question'))
        self.assertQuerysetEqual(response.context['object_list'], questions, ordered=False)

        response = self.client.get(reverse('myadmin:admins_search_results_question'),
                                   {'admins_search_panel': '6'})

        questions = Question.objects.filter(Q(question__icontains='6') | Q(tag__icontains='6'))
        self.assertQuerysetEqual(response.context['object_list'], questions, ordered=False)


class TestAdminsSearchPostView(TestAdminOneUserOneCategory):
    """AdminsSearchPostView test."""

    def setUp(self):
        """Creating test user, post and category objects."""
        super().setUp()
        for number in range(1, 8):
            Post.objects.create(title=f'post_{number}',
                                author=self.test_user,
                                category=self.test_category,
                                body='some text',
                                available=True)

    def test_view_authorized_users_only(self):
        """Checks that view and relevant site page are not available to unauthorized users."""
        response = self.client.get('/myadmin/search/post/')
        self.assertEqual(response.url, '/users/login/?next=/myadmin/search/post/')
        self.assertEqual(response.status_code, 302)

    def test_view_superusers_only(self):
        """Checks that AdminsSearchPostView view and relevant site page are only available to superusers."""
        self.test_user.is_superuser = False
        self.test_user.save()
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/myadmin/search/post/')
        self.assertEqual(response.url, '/users/login/?next=/myadmin/search/post/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_exists_at_desired_location(self):
        """Checks that the view URL exists in the desired location."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/myadmin/search/post/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Checks if the view URL is available by name."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_search_results_post'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template_and_title(self):
        """Checks that the view uses the correct template and title."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_search_results_post'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myadmin/posts/search_results_post.html')
        self.assertEqual(response.context['title'], 'Поиск статьи')

    def test_view_returns_correctly_filtered_queryset(self):
        """Checks that view returns a correctly filtered queryset."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('myadmin:admins_search_results_post'),
                                   {'admins_search_panel': 'post'})

        posts = Post.objects.filter(Q(title__icontains='post') | Q(tag__icontains='post'))
        self.assertQuerysetEqual(response.context['object_list'], posts, ordered=False)

        response = self.client.get(reverse('myadmin:admins_search_results_post'),
                                   {'admins_search_panel': '6'})

        posts = Post.objects.filter(Q(title__icontains='6') | Q(tag__icontains='6'))
        self.assertQuerysetEqual(response.context['object_list'], posts, ordered=False)
