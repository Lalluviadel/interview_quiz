"""
Contains unit and integration tests for checking the views of the web application.
"""

import logging
import sys

from django.db.models import Q
from django.test import TestCase, Client
from django.urls import reverse

from interview_quiz import settings
from interview_quiz.variabls import POINTS_LEVEL
from posts.models import Post
from users.models import MyUser
from ..models import QuestionCategory, Question

if len(sys.argv) > 1 and sys.argv[1] == 'test':
    logging.disable(logging.CRITICAL)


class TestMainView(TestCase):
    """MainView test."""

    def setUp(self):
        self.client = Client()

    def test_view_url_exists_at_desired_location(self):
        """Checks that the view URL exists in the desired location."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Checks if the view URL is available by name."""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template_and_title(self):
        """Checks that the view uses the correct template and title."""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questions/index.html')
        self.assertEqual(response.context['title'], 'Interview challenge')


class TestAllCategoriesView(TestCase):
    """AllCategoriesView test."""

    def setUp(self):
        """Creating 10 test categories, objects with even IDs are not available."""
        self.client = Client()
        for number in range(10):
            item = QuestionCategory.objects.create(name=f'category_{number}', description=f'description_{number}')
            if number % 2 == 0:
                item.available = False
                item.save()

    def test_view_url_exists_at_desired_location(self):
        """Checks that the view URL exists in the desired location."""
        response = self.client.get('/questions/categories/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Checks if the view URL is available by name."""
        response = self.client.get(reverse('questions:categories'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template_and_title(self):
        """Checks that the view uses the correct template and title."""
        response = self.client.get(reverse('questions:categories'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questions/categories.html')
        self.assertEqual(response.context['title'], 'Категории тестов')

    def test_view_queryset_only_available_categories(self):
        """Tests that only the available categories fall into the queryset."""
        response = self.client.get(reverse('questions:categories'))
        for item in response.context['questioncategory_list']:
            self.assertTrue(item.available)
        self.assertTrue(len(response.context['questioncategory_list']) == 5)


class TestBase(TestCase):
    """Parent test class for observing the DRY pattern."""

    def setUp(self):
        """Creating test category and user objects."""
        self.client = Client()
        self.test_user = MyUser.objects.create_user(username='test_01',
                                                    first_name='Roland',
                                                    last_name='Emmerich',
                                                    email='blabla@bla.ru',
                                                    is_active=True)
        self.test_user.set_password('laLA12')
        self.test_user.save()
        self.test_category = QuestionCategory.objects.create(name='Disasters')


class TestCategoryView(TestBase):
    """CategoryView test."""

    def setUp(self):
        super().setUp()

    def test_view_authorized_users_only(self):
        """Checks that CategoryView view and relevant site page are only available to authorized users."""
        response = self.client.get(f'/questions/start_test/{self.test_category.id}/')
        self.assertEqual(response.url, f'/users/login/?next=/questions/start_test/{self.test_category.id}/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_exists_at_desired_location(self):
        """Checks that the view URL exists in the desired location."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(f'/questions/start_test/{self.test_category.id}/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Checks if the view URL is available by name."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('questions:start_test', args=[self.test_category.id]))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template_and_title(self):
        """Checks that the view uses the correct template and title."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('questions:start_test', args=[self.test_category.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questions/start_test.html')
        self.assertEqual(response.context['title'], f'Категория {self.test_category.name}')

    def test_view_get_context_data_works_correctly(self):
        """Checks the correctness of receiving and transmitting data to the context:
        the current user, the current category of questions, the numeric value of the info field of the user object."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('questions:start_test', args=[self.test_category.id]))
        self.assertEqual(self.test_user, response.context['user'])
        self.assertEqual(int(self.test_user.info), response.context['user_info'])
        self.assertEqual(self.test_category, response.context['category'])


class TestQuestionView(TestBase):
    """QuestionView test."""

    def setUp(self):
        super().setUp()

    def test_view_authorized_users_only(self):
        """Checks that QuestionView view and relevant site page are only available to authorized users."""
        response = self.client.post(f'/questions/test_body/{self.test_category.id}/')
        self.assertEqual(response.url, f'/users/login/?next=/questions/test_body/{self.test_category.id}/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_exists_at_desired_location(self):
        """Checks that the view URL exists in the desired location."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.post(f'/questions/test_body/{self.test_category.id}/',
                                    {'csrf_data': 'some data', 'options_dif': 'NB', 'options_y_n': 'False'})
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Checks if the view URL is available by name."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.post(reverse('questions:test_body', args=[self.test_category.id]),
                                    {'csrf_data': 'some data', 'options_dif': 'NB', 'options_y_n': 'False'})
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template_and_title(self):
        """Checks that the view uses the correct template and title."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.post(reverse('questions:test_body', args=[self.test_category.id]),
                                    {'csrf_data': 'some data', 'options_dif': 'NB', 'options_y_n': 'False'})
        self.assertTemplateUsed(response, 'questions/test_body.html')
        self.assertEqual(response.context['title'], f'Тест по категории {self.test_category.name}')

    def test_get_question_queryset_more_20(self):
        """A test for the case when the questions of the selected category and difficulty level are more than 20.
        Checks:
        - that the question ready for display is in context and has a Question class;
        - that the queryset of the remaining questions is in the context of the session
        and its length by the beginning of the test is 19 (20 - 1 question ready for issue);
        - that all questions in the queryset are unique;
        - that the question ready for issue is also unique;
        """
        for number in range(25):
            Question.objects.create(question=f'test_question_{number}', subject=self.test_category,
                                    author=self.test_user, right_answer=f'{number}', available=True,
                                    answer_01=f'{number}', answer_02=f'{number + 1}', answer_03=f'{number + 2}',
                                    answer_04=f'{number + 3}')
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.post(reverse('questions:test_body', args=[self.test_category.id]),
                                    {'csrf_data': 'some data', 'options_dif': 'NB', 'options_y_n': 'False'})

        question_used_now = response.context['item']
        self.assertIsInstance(question_used_now, Question)

        session_question_set = self.client.session['context']['question_set']
        self.assertEqual(len(session_question_set), 19)

        self.assertEqual(len(session_question_set), len(set(session_question_set)))
        self.assertNotIn(question_used_now.id, session_question_set)

    def test_get_question_queryset_less_20(self):
        """A test for the case when the questions of the selected category and difficulty level are less than 20.
        Checks:
        - that the question ready for display is in context and has a Question class;
        - that the queryset of the remaining questions is in the context of the session
        and its length by the beginning of the test is 5 (6 - 1 question ready for issue);
        - that all questions in the queryset are unique;
        - that the question ready for issue is also unique;
        """
        for number in range(6):
            Question.objects.create(question=f'test_question_{number}',
                                    subject=self.test_category, author=self.test_user,
                                    right_answer=f'{number}', available=True,
                                    answer_01=f'{number}', answer_02=f'{number + 1}',
                                    answer_03=f'{number + 2}', answer_04=f'{number + 3}')

        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.post(reverse('questions:test_body', args=[self.test_category.id]),
                                    {'csrf_data': 'some data', 'options_dif': 'NB', 'options_y_n': 'False'})

        session_question_set = self.client.session['context']['question_set']
        self.assertEqual(len(session_question_set), 5)

        question_used_now = response.context['item']
        self.assertIsInstance(question_used_now, Question)

        self.assertEqual(len(session_question_set), len(set(session_question_set)))
        self.assertNotIn(question_used_now.id, session_question_set)

    def test_uniqueness_question_queryset_more_20(self):
        """The test is for the case when the number of questions of a given category
        and difficulty level is more than 20.
        Checks that the queryset of questions is different each time.
        There is still some chance of a failed test, since queryset can theoretically be repeated"""
        self.client.login(username=self.test_user.username, password='laLA12')
        for number in range(25):
            Question.objects.create(question=f'test_question_{number}', subject=self.test_category,
                                    author=self.test_user, right_answer=f'{number}', available=True,
                                    answer_01=f'{number}', answer_02=f'{number + 1}',
                                    answer_03=f'{number + 2}', answer_04=f'{number + 3}')

        self.client.post(reverse('questions:test_body', args=[self.test_category.id]),
                         {'csrf_data': 'some data', 'options_dif': 'NB', 'options_y_n': 'False'})
        session_question_set_01 = self.client.session['context']['question_set']
        self.client.post(reverse('questions:test_body', args=[self.test_category.id]),
                         {'csrf_data': 'some data', 'options_dif': 'NB', 'options_y_n': 'False'})
        session_question_set_02 = self.client.session['context']['question_set']
        self.assertNotEqual(session_question_set_01, session_question_set_02)

    def test_uniqueness_question_queryset_less_20(self):
        """The test is for the case when the number of questions of a given category
        and difficulty level is less than 20.
        Checks that the queryset of questions is different each time.
        There is still some chance of a failed test, since queryset can theoretically be repeated."""
        self.client.login(username=self.test_user.username, password='laLA12')
        for number in range(9):
            Question.objects.create(question=f'test_question_{number}',
                                    subject=self.test_category, author=self.test_user,
                                    right_answer=f'{number}', available=True,
                                    answer_01=f'{number}', answer_02=f'{number + 1}',
                                    answer_03=f'{number + 2}', answer_04=f'{number + 3}')

        self.client.post(reverse('questions:test_body', args=[self.test_category.id]),
                         {'csrf_data': 'some data', 'options_dif': 'NB', 'options_y_n': 'False'})
        session_question_set_01 = self.client.session['context']['question_set']
        self.client.post(reverse('questions:test_body', args=[self.test_category.id]),
                         {'csrf_data': 'some data', 'options_dif': 'NB', 'options_y_n': 'False'})
        session_question_set_02 = self.client.session['context']['question_set']
        self.assertNotEqual(session_question_set_01, session_question_set_02)

    def test_view_post_request_context(self):
        """Checks the correctness of receiving and transmitting data to the request context."""
        self.client.login(username=self.test_user.username, password='laLA12')
        for number in range(25):
            Question.objects.create(question=f'test_question_{number}',
                                    subject=self.test_category, author=self.test_user,
                                    right_answer=f'{number}', available=True,
                                    answer_01=f'{number}', answer_02=f'{number + 1}',
                                    answer_03=f'{number + 2}', answer_04=f'{number + 3}')
        difficulty_level, time_limit = 'NB', 'False'
        response = self.client.post(reverse('questions:test_body', args=[self.test_category.id]),
                                    {'csrf_data': 'some data', 'options_dif': difficulty_level,
                                     'options_y_n': time_limit})

        self.assertIn('item', response.context)
        self.assertEqual(response.context['dif_points'], POINTS_LEVEL[difficulty_level])
        self.assertEqual(response.context['limit'], time_limit)
        self.assertEqual(response.context['current_category'], self.test_category.name)
        self.assertEqual(response.context['title'], f'Тест по категории {self.test_category.name}')
        self.assertEqual(response.context['dif'], difficulty_level)
        self.assertEqual(response.context['quantity'], len(self.client.session['context']['question_set']) + 1)
        self.assertEqual(response.context['right_ans'], 0)
        self.assertEqual(response.context['wrong_ans'], 0)
        self.assertEqual(response.context['category'], self.test_category)
        self.assertEqual(response.context['user_points'], self.test_user.score)

    def test_view_post_session_context(self):
        """Checks the correctness of receiving and transmitting data to the session context."""
        for number in range(25):
            Question.objects.create(question=f'test_question_{number}',
                                    subject=self.test_category, author=self.test_user,
                                    right_answer=f'{number}', available=True,
                                    answer_01=f'{number}', answer_02=f'{number + 1}',
                                    answer_03=f'{number + 2}', answer_04=f'{number + 3}')
        self.client.login(username=self.test_user.username, password='laLA12')
        difficulty_level, time_limit = 'NB', 'False'
        self.client.post(reverse('questions:test_body', args=[self.test_category.id]),
                         {'csrf_data': 'some data', 'options_dif': difficulty_level, 'options_y_n': time_limit})

        context = self.client.session['context']
        self.assertEqual(context['dif_points'], POINTS_LEVEL[difficulty_level])
        self.assertEqual(context['limit'], time_limit)
        self.assertEqual(context['current_category'], self.test_category.name)
        self.assertEqual(context['title'], f'Тест по категории {self.test_category.name}')
        self.assertEqual(context['dif'], difficulty_level)
        self.assertEqual(context['quantity'], len(self.client.session['context']['question_set']) + 1)
        self.assertEqual(context['right_ans'], 0)
        self.assertEqual(context['wrong_ans'], 0)
        self.assertEqual(len(context['question_set']), 19)

    def test_continuation_of_examination(self):
        """Checks the correctness of continuing user's testing, transferring data to the context,
        reducing the number of questions in the queryset, changing the current question."""
        self.client.login(username=self.test_user.username, password='laLA12')
        difficulty_level, time_limit = 'NB', 'False'
        for number in range(25):
            Question.objects.create(question=f'test_question_{number}',
                                    subject=self.test_category, author=self.test_user,
                                    right_answer=f'{number}', available=True,
                                    answer_01=f'{number}', answer_02=f'{number + 1}',
                                    answer_03=f'{number + 2}', answer_04=f'{number + 3}')
        response_test_01 = self.client.post(reverse('questions:test_body', args=[self.test_category.id]),
                                            {'csrf_data': 'some data', 'options_dif': difficulty_level,
                                             'options_y_n': time_limit})

        question_01 = response_test_01.context['item']

        session_context = self.client.session['context']
        self.assertEqual(len(session_context['question_set']), 19)

        self.client.get(reverse('questions:answers', args=[question_01.id]),
                        {'csrf_data': 'some data', 'answers': question_01.right_answer},
                        kwargs={'item_id': question_01.id})

        response_test_02 = self.client.get(reverse('questions:test_body', kwargs={'pk': self.test_category.id}))
        question_02 = response_test_02.context['item']

        session_context = self.client.session['context']
        self.assertEqual(len(session_context['question_set']), 18)
        self.assertNotEqual(question_01, question_02)

        self.assertIn('item', response_test_02.context)
        self.assertEqual(response_test_02.context['category'], self.test_category)

        user = MyUser.objects.get(id=self.test_user.id)
        self.assertEqual(response_test_02.context['user_points'], user.score)


class TestAnswerQuestion(TestBase):
    """AnswerQuestion view test."""

    def setUp(self):
        """Creating test category, questions and user objects, sending a POST request at the start of testing."""
        super().setUp()
        for number in range(1, 25):
            Question.objects.create(question=f'test_question_{number}',
                                    subject=self.test_category, author=self.test_user,
                                    right_answer=f'{number}', available=True,
                                    answer_01=f'{number}', answer_02=f'{number + 1}',
                                    answer_03=f'{number + 2}', answer_04=f'{number + 3}',
                                    difficulty_level='AV')

        self.client.login(username=self.test_user.username, password='laLA12')
        difficulty_level, time_limit = 'AV', 'False'
        self.response = self.client.post(reverse('questions:test_body', args=[self.test_category.id]),
                                         {'csrf_data': 'some data', 'options_dif': difficulty_level,
                                          'options_y_n': time_limit})
        self.question_id = self.response.context['item'].id
        self.right_answer = self.response.context['item'].right_answer

    def test_view_authorized_users_only(self):
        """Checks that AnswerQuestion view and relevant site page are only available to authorized users."""
        self.client.logout()
        response = self.client.get(f'/questions/answers/{self.question_id}/')
        self.assertEqual(response.url, f'/users/login/?next=/questions/answers/{self.question_id}/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_exists_at_desired_location(self):
        """Checks that the view URL exists in the desired location."""
        response = self.client.get(f'/questions/answers/{self.question_id}/',
                                   {'csrf_data': 'some data', 'answers': self.right_answer}, kwargs={self.question_id})
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Checks if the view URL is available by name."""
        response = self.client.get(reverse('questions:answers', args=[self.test_category.id]),
                                   {'csrf_data': 'some data', 'answers': self.right_answer}, kwargs={self.question_id})
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template_and_title(self):
        """Checks that the view uses the correct template and title."""
        response = self.client.get(reverse('questions:answers', args=[self.question_id]),
                                   {'csrf_data': 'some data', 'answers': self.right_answer},
                                   kwargs={'item_id': self.question_id})
        item = self.response.context['item']
        self.assertTemplateUsed(response, 'questions/answers.html')
        self.assertEqual(response.context['title'], f'Ответ на вопрос {item}')

    def test_user_answered_correctly(self):
        """Checks that when user answered correctly, the user's score increases
        in accordance with the scores of the difficulty level of the question,
        and the number of correct answers stored in the context of the session increases by 1."""
        self.client.get(reverse('questions:answers', args=[self.question_id]),
                        {'csrf_data': 'some data', 'answers': self.right_answer},
                        kwargs={'item_id': self.question_id})
        user = MyUser.objects.get(id=self.test_user.id)
        self.assertEqual(user.score, 2)

        session_context = self.client.session['context']
        self.assertEqual(session_context['right_ans'], 1)
        self.assertEqual(session_context['wrong_ans'], 0)

    def test_user_answered_incorrectly_score_is_0(self):
        """Checks that if the user answered incorrectly and his score less than the points for the answer,
        it will not decrease.
        The number of incorrect responses stored in the context of the session increases by 1."""
        user = MyUser.objects.get(id=self.test_user.id)
        user.score = 1
        user.save()

        self.client.get(reverse('questions:answers', args=[self.question_id]),
                        {'csrf_data': 'some data', 'answers': 'some kind of wrong answer'},
                        kwargs={'item_id': self.question_id})
        user = MyUser.objects.get(id=self.test_user.id)
        self.assertEqual(user.score, 0)

        session_context = self.client.session['context']
        self.assertEqual(session_context['right_ans'], 0)
        self.assertEqual(session_context['wrong_ans'], 1)

    def test_user_answered_incorrectly_score_more_0(self):
        """Checks that if the user answered incorrectly and his score is greater than 0,
        it will decrease by the number of points according to the difficulty level of the question.
        The number of incorrect responses stored in the context of the session increases by 1."""
        user = MyUser.objects.get(id=self.test_user.id)
        user.score = 15
        user.save()
        self.client.get(reverse('questions:answers', args=[self.question_id]),
                        {'csrf_data': 'some data', 'answers': 'some kind of wrong answer'},
                        kwargs={'item_id': self.question_id})
        self.assertEqual(MyUser.objects.get(id=self.test_user.id).score, 13)
        session_context = self.client.session['context']
        self.assertEqual(session_context['right_ans'], 0)
        self.assertEqual(session_context['wrong_ans'], 1)

        self.client.get(reverse('questions:answers', args=[self.question_id]),
                        {'csrf_data': 'some data', 'answers': 'some kind of wrong answer'},
                        kwargs={'item_id': self.question_id})
        self.assertEqual(MyUser.objects.get(id=self.test_user.id).score, 11)
        session_context = self.client.session['context']
        self.assertEqual(session_context['right_ans'], 0)
        self.assertEqual(session_context['wrong_ans'], 2)

    def test_view_get_request_context(self):
        """Checks the correctness of receiving and transmitting data to the request context."""
        for number in range(5):
            Post.objects.create(title=f'test_post_{number}',
                                author=self.test_user,
                                category=self.test_category,
                                body='some text',
                                tag='IT',
                                available=True)
        not_available_post = Post.objects.get(title=f'test_post_3')
        not_available_post.available = False
        not_available_post.save()

        question = Question.objects.get(id=self.question_id)
        posts = Post.objects.filter(Q(tag=question.tag), Q(available=True))

        response = self.client.get(reverse('questions:answers', args=[self.question_id]),
                                   {'csrf_data': 'some data', 'answers': self.right_answer},
                                   kwargs={'item_id': self.question_id})
        self.assertEqual(response.context['title'], f'Ответ на вопрос {question}')
        self.assertEqual(response.context['item'], question)
        self.assertEqual(response.context['chosen_answer'], self.right_answer)
        self.assertTrue(response.context['guessed'])
        self.assertEqual(response.context['user'], self.test_user)
        self.assertEqual(len(response.context['posts']), 4)
        self.assertEqual(set(response.context['posts']), set(posts))

        for post in response.context['posts']:
            self.assertTrue(post.available)


class TestQuestionAndAnswerView(TestCase):
    """A test of the full testing process."""

    def setUp(self):
        """Creating test category, questions and user objects,
        making requests to start testing and verify the first answer."""
        self.client = Client()
        self.test_user = MyUser.objects.create_user(username='test_01',
                                                    first_name='Roland',
                                                    last_name='Emmerich',
                                                    email='blabla@bla.ru',
                                                    is_active=True)
        self.test_user.set_password('laLA12')
        self.test_user.save()
        self.client.login(username=self.test_user.username, password='laLA12')

        self.test_category = QuestionCategory.objects.create(name='Disasters')

        for number in range(25):
            Question.objects.create(question=f'test_question_{number}',
                                    subject=self.test_category, author=self.test_user,
                                    right_answer=f'{number}', available=True,
                                    answer_01=f'{number}', answer_02=f'{number + 1}',
                                    answer_03=f'{number + 2}', answer_04=f'{number + 3}')

        time_limit, difficulty_level = 'False', 'NB'
        response_start_test = self.client.post(reverse('questions:test_body', args=[self.test_category.id]),
                                               {'csrf_data': 'some data', 'options_dif': difficulty_level,
                                                'options_y_n': time_limit})

        question_01 = response_start_test.context['item']
        self.client.get(reverse('questions:answers', args=[question_01.id]),
                        {'csrf_data': 'some data', 'answers': question_01.right_answer},
                        kwargs={'item_id': question_01.id})

    def test_examination_process(self):
        """Performs the entire user testing process, starting with the second question,
        completes testing, checks the current number of user points, the number of correct/incorrect answers,
        the absence of unanswered questions."""
        session_context = self.client.session['context']

        for item in session_context['question_set'][::-1]:
            self.client.get(reverse('questions:test_body', kwargs={'pk': self.test_category.id}))
            right_answer = Question.objects.get(id=item).right_answer
            self.client.get(reverse('questions:answers', args=[item]),
                            {'csrf_data': 'some data', 'answers': right_answer},
                            kwargs={'item_id': item})

        session_context = self.client.session['context']
        user = MyUser.objects.get(id=self.test_user.id)
        self.assertEqual(user.score, 20)
        self.assertEqual(session_context['right_ans'], 20)
        self.assertEqual(session_context['wrong_ans'], 0)
        self.assertEqual(len(session_context['question_set']), 0)

        response_test_end = self.client.get(reverse('questions:test_body', kwargs={'pk': self.test_category.id}))
        self.assertEqual(response_test_end.context['item'], 'Stop')


class TestTimeIsUp(TestCase):
    """TimeIsUp test."""

    def setUp(self):
        self.client = Client()
        self.test_user = MyUser.objects.create_user(username='test_01',
                                                    first_name='Roland',
                                                    last_name='Emmerich',
                                                    email='blabla@bla.ru',
                                                    is_active=True)
        self.test_user.set_password('laLA12')
        self.test_user.save()

    def test_view_authorized_users_only(self):
        """Checks that TimeIsUp view and relevant site page are only available to authorized users."""
        response = self.client.get('/questions/time_is_up/')
        self.assertEqual(response.url, f'/users/login/?next=/questions/time_is_up/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_exists_at_desired_location(self):
        """Checks that the view URL exists in the desired location."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get('/questions/time_is_up/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Checks if the view URL is available by name."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('questions:time_is_up'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template_and_title(self):
        """Checks that the view uses the correct template and title."""
        self.client.login(username=self.test_user.username, password='laLA12')
        response = self.client.get(reverse('questions:time_is_up'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'questions/time_is_up.html')
        self.assertEqual(response.context['title'], 'Время вышло')


if settings.DEBUG:

    class Test404Page(TestCase):
        """Custom handler404 test."""

        def test_view_url_exists_at_desired_location(self):
            """Checks that the view URL exists in the desired location."""
            response = self.client.get('/404/')
            self.assertEqual(response.status_code, 404)

        def test_view_uses_correct_template_and_title(self):
            """Checks that the view uses the correct template and title."""
            response = self.client.get('/404/')
            self.assertEqual(response.status_code, 404)
            self.assertTemplateUsed(response, 'questions/page_not_found.html')
            self.assertEqual(response.context['title'], '404: Страница не существует')
