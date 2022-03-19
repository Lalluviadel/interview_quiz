import logging
from random import randint

from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, TemplateView, DetailView

from interview_quiz.mixin import TitleMixin, AuthorizedOnlyDispatchMixin
from interview_quiz.variabls import POINTS_LEVEL
from posts.models import Post
from questions.models import Question, QuestionCategory
from users.models import MyUser

logger = logging.getLogger(__name__)


class MainView(TemplateView, TitleMixin):
    template_name = 'questions/index.html'
    title = 'Interview challenge'


class AllCategoriesView(ListView, TitleMixin):
    model = QuestionCategory
    template_name = 'questions/categories.html'
    title = 'Категории тестов'

    def get_queryset(self):
        return QuestionCategory.objects.filter(available=True)


class CategoryView(DetailView):
    model = QuestionCategory
    template_name = 'questions/start_test.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        current_category = get_object_or_404(QuestionCategory, pk=self.kwargs.get('pk'))
        context['category'] = current_category
        context['title'] = f'Категория {current_category.name}'
        return context


class QuestionView(DetailView, AuthorizedOnlyDispatchMixin):
    model = Question
    template_name = 'questions/test_body.html'

    def post(self, request, *args, **kwargs):
        data = list(request.POST.values())
        self.request.session['dif'] = difficulty_level = data[1]
        self.request.session['limit'] = data[2]

        current_category = get_object_or_404(QuestionCategory, pk=self.kwargs.get('pk'))
        question_set = self.get_question_set(current_category, difficulty_level)
        id_list = [item.id for item in question_set]

        context = {'dif_points': POINTS_LEVEL[difficulty_level],
                   'title': f'Тест по категории {current_category.name}',
                   'limit': self.request.session['limit'],
                   'dif': difficulty_level,
                   'quantity': len(id_list),
                   'right_ans': 0,
                   'wrong_ans': 0,
                   }
        self.request.session['context'] = context

        context_upd = context.copy()
        context_upd['category'] = current_category
        context_upd['item'] = Question.objects.get(id=id_list.pop())
        context['question_set'] = id_list
        context_upd['user_points'] = self.request.user.score

        return render(request, 'questions/test_body.html', context=context_upd)

    def get(self, request, *args, **kwargs):
        current_category = get_object_or_404(QuestionCategory, pk=self.kwargs.get('pk'))
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
        return render(request, 'questions/test_body.html', context=context_current)

    @staticmethod
    def get_question_set(category, diff_level):
        question_set = Question.objects.filter(Q(subject=category), Q(difficulty_level=diff_level), Q(available=True))
        if question_set.count() < 20:
            return question_set
        result_set = list()
        while len(result_set) < 20:
            try:
                result_set.append(question_set[randint(1, (len(question_set)) - 1)])
            except ValueError:
                logger.error('Ошибка запроса вопроса из базы')
                return None
        return result_set


class AnswerQuestion(DetailView, AuthorizedOnlyDispatchMixin):
    model = Question
    template_name = 'questions/answers.html'

    def get(self, request, guessed=False, *args, **kwargs):
        difficult_level = self.request.session['dif']
        chosen_answer = list(request.GET.values())[1]
        item = Question.objects.get(id=kwargs['item_id'])
        posts = Post.objects.filter(tag=item.tag)[:4]
        user = MyUser.objects.get(id=request.user.id)

        if chosen_answer == item.right_answer:
            guessed = True
            request.session['context']['right_ans'] += 1
            user.score += POINTS_LEVEL[difficult_level]
        else:
            request.session['context']['wrong_ans'] += 1
            if user.score > 0:
                user.score -= POINTS_LEVEL[difficult_level]
        request.session.modified = True
        user.save()
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
    template_name = 'questions/time_is_up.html'
    title = 'Время вышло'
