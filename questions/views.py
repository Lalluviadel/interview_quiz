"""
Views for working with objects of questions and categories.

The submodule contains views for working with objects of questions
and categories. Within this submodule, the main actions of the entire
project take place:
* the formation of a set of test questions;
* ensuring its passage by the user;
* accrual or withdrawal of points.

Here are views:

    * to display the main page of the site;
    * to intercept the 404 error code;
    * to display all categories;
    * to display the initial page of the text,
        for the process; ; its passage and getting the result;
    * when passing a test with a time limit - for the end
        of the test after the expiration of time;

"""


import logging
from random import randint

from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView, TemplateView

from interview_quiz.mixin import AuthorizedOnlyDispatchMixin, TitleMixin
from interview_quiz.variabls import POINTS_LEVEL

from posts.models import Post

from questions.models import Question, QuestionCategory

from users.models import MyUser

logger = logging.getLogger(__name__)


def my_handler404(request, exception):
    """View for the 404 page."""
    context = {'title': '404: Страница не существует'}
    response = render(
        request, 'questions/page_not_found.html', context=context
    )
    response.status_code = 404
    return response


class MainView(TemplateView, TitleMixin):
    """View for the main page."""

    template_name = 'questions/index.html'
    title = 'Interview challenge'


class AllCategoriesView(ListView, TitleMixin):
    """View for the categories of questions page."""

    model = QuestionCategory
    template_name = 'questions/categories.html'
    title = 'Категории тестов'

    def get_queryset(self):
        """Return queryset of only available categories."""
        return QuestionCategory.objects.filter(available=True)


class CategoryView(DetailView, AuthorizedOnlyDispatchMixin):
    """View for a specific category page."""

    model = QuestionCategory
    template_name = 'questions/start_test.html'

    def get_context_data(self, *args, **kwargs):
        """
        Form context of the category page.

        Generates and returns the context for the correct substitution
        of data on the category page.
        Adds 'user_info' to the context - it depends on whether the user
        will be shown a modal window with testing information. Initially,
        such an alert is shown to all users, but if the user wants to no
        longer see this window, he puts a check mark in the checkbox,
        changing the data in the 'user_info' field of his instance of the
        MyUser model.
        """
        context = super().get_context_data(**kwargs)
        user = MyUser.objects.get(id=self.request.user.id)
        current_category = get_object_or_404(
            QuestionCategory, pk=self.kwargs.get('pk')
        )
        context['category'] = current_category

        try:
            context['user_info'] = int(user.info)
        except ValueError:
            logger.error(
                'Ошибка обработки значения поля user_info модели MyUser'
            )
        context['title'] = f'Категория {current_category.name}'
        return context


class QuestionView(DetailView, AuthorizedOnlyDispatchMixin):
    """
    View for the testing process.

    Generates a pseudo-random list of questions of the
    specified category and complexity. Stores a queryset
    of questions, the number of correct and incorrect answers,
    and source data during testing.
    """

    model = Question
    template_name = 'questions/test_body.html'

    def post(self, request, *args, **kwargs):
        """
        Receives and generates the starting data.

            * the selected difficulty level;
            * the presence or absence of a time limit for the answer;
            * the selected category;
            * a set of questions.

        Data is saved both to the current presentation context and
        to the session for storing and updating them during the test process
        (MemCached (PyMemcacheCache) is used as a cache).
        """
        data = list(request.POST.values())
        self.request.session['dif'] = difficulty_level = data[1]
        self.request.session['limit'] = data[2]

        current_category = get_object_or_404(
            QuestionCategory, pk=self.kwargs.get('pk')
        )
        question_set = self.get_question_set(
            current_category, difficulty_level
        )
        id_list = [item.id for item in question_set]
        context = {'dif_points': POINTS_LEVEL[difficulty_level],
                   'title': f'Тест по категории {current_category.name}',
                   'current_category': current_category.name,
                   'limit': self.request.session['limit'],
                   'dif': difficulty_level,
                   'quantity': len(id_list),
                   'right_ans': 0,
                   'wrong_ans': 0,
                   }
        self.request.session['context'] = context

        context_upd = context.copy()
        context_upd['category'] = current_category
        if id_list:
            context_upd['item'] = Question.objects.get(id=id_list.pop())
            context['question_set'] = id_list
        context_upd['user_points'] = self.request.user.score

        return render(request, 'questions/test_body.html', context=context_upd)

    def get(self, request, *args, **kwargs):
        """
        Provide continuation and termination of user testing.

        Performs a reduction in the number of questions in
        the queryset stored in the session, ensures the change
        of the current question, completes testing when the queryset
        of questions is exhausted.
        """
        current_category = get_object_or_404(
            QuestionCategory, pk=self.kwargs.get('pk')
        )
        context = self.request.session['context']
        context_current = context.copy()
        id_list = context['question_set']
        if len(id_list) > 0:
            context_current['item'] = Question.objects.get(id=id_list.pop())
            request.session['context']['question_set'] = id_list
            request.session.modified = True
        else:
            context_current['item'] = 'Stop'
        context_current['category'] = current_category
        context_current['user_points'] = self.request.user.score
        return render(
            request, 'questions/test_body.html',
            context=context_current
        )

    @staticmethod
    def get_question_set(category, diff_level):
        """
        Generate a queryset.

        Generates a queryset of all available questions of the
        desired category and level of complexity; receives and returns
        a pseudo-random queryset of 20 questions if the original
        queryset was more than 20, or in an amount equal to the number
        of questions of the original queryset.

        Args:
            * category(QuestionCategory): user-selected question category;
            * diff_level(Question.difficulty_level): user-selected
                difficulty level;

        Return:
            * result_set(list): a pseudo-random list of Question objects
                - questions of the selected category and difficulty level,
                are available for use.
        """
        question_set = Question.objects.filter(
            Q(subject=category),
            Q(difficulty_level=diff_level),
            Q(available=True)
        )
        question_set_count = question_set.count()
        if question_set_count < 20:
            return QuestionView.create_random_queryset(
                question_set, question_set_count, question_set_count
            )
        return QuestionView.create_random_queryset(
            question_set, question_set_count
        )

    @staticmethod
    def create_random_queryset(question_set, question_set_count, limit=20):
        """
        Generate a pseudo-random queryset of questions.

        Generates a pseudo-random queryset of questions in an
        amount equal to the specified limit and returns it.

        Args:
            * question_set(Queryset of Question objects):
                queryset of all questions of the selected category,
                difficulty level and available for use;
            * question_set_count(int):
                the number of questions in this queryset;
            * limit(int, optional):
                the default value is 20. Limits the number of questions
                per test. If less than 20 questions belong to the
                selected category and difficulty level, the limit
                value will be equal to their number.

        Return:
            * result_set(list): a pseudo-random list of Question objects
                - questions of the selected category and difficulty level,
                are available for use.
        """
        result_set = []
        while len(result_set) < limit:
            try:
                item = question_set[randint(0, question_set_count - 1)]
                if item not in result_set:
                    result_set.append(item)
            except ValueError:
                logger.error('Ошибка запроса вопроса из базы')
                return None
        return result_set


class AnswerQuestion(DetailView, AuthorizedOnlyDispatchMixin):
    """
    Check the correctness of the answer.

    View to check the correctness of the answer and
    increase/decrease the player's score and the number of his
    correct and incorrect answers stored in the session.
    """

    model = Question
    template_name = 'questions/answers.html'

    def get(self, request, guessed=False, *args, **kwargs):
        """
        Check the correctness of this answer.

        Checks the correctness of this answer and increases/
        decreases the player's score and the number of his correct
        and incorrect answers stored in the session.
        If the player's score is less than or equal to the number
        of points for the answer, his score will be zero.

        Args:
            * request: standard parameter.
            * guessed(bool): information about whether the question
                has been guessed;
            * ``*args``: standard parameter.
            * ``**kwargs``: standard parameter.
        """
        difficult_level = self.request.session['dif']
        chosen_answer = list(request.GET.values())[1]
        item = Question.objects.get(id=kwargs['item_id'])
        posts = Post.objects.filter(
            Q(tag=item.tag) & Q(available=True))[:4].defer(
            'author', 'category', 'body', 'image', 'created_on'
        )
        user = MyUser.objects.get(id=request.user.id)
        points = POINTS_LEVEL[difficult_level]

        if chosen_answer == item.right_answer:
            guessed = True
            request.session['context']['right_ans'] += 1
            user.score += points
        else:
            request.session['context']['wrong_ans'] += 1
            if user.score >= points:
                user.score -= points
            else:
                user.score = 0
        request.session.modified = True
        user.save(update_fields=['score'])
        context = {
            'title': f'Ответ на вопрос {item}',
            'item': item,
            'chosen_answer': chosen_answer,
            'guessed': guessed,
            'user': user,
            'posts': posts,
        }
        return render(request, 'questions/answers.html', context)


class TimeIsUp(TemplateView, TitleMixin, AuthorizedOnlyDispatchMixin):
    """
    View of the end of the time for reflection.

    A view for the page of the end of the time for reflection,
    if the user has chosen a time limit for each response.
    The test is interrupted regardless of whether there are
    unanswered questions.
    """

    template_name = 'questions/time_is_up.html'
    title = 'Время вышло'
