from random import randint

from django.db.models import Max
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView

from posts.models import Post
from questions.models import Question, QuestionCategory


def index(request):
    context = {
        'title': 'Interview challenge',
    }
    return render(request, 'questions/index.html', context)


def categories(request):
    context = {
        'title': 'Категории тестов',
    }
    return render(request, 'questions/categories.html', context)


class CategoryView(ListView):
    model = QuestionCategory
    template_name = 'questions/start_test.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        current_category = get_object_or_404(QuestionCategory, pk=self.kwargs.get('pk'))
        context['category'] = current_category
        context['title'] = f'Категория {current_category.name}'
        return context


class QuestionView(ListView):
    model = Question
    template_name = 'questions/test_body.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        current_category = get_object_or_404(QuestionCategory, pk=self.kwargs.get('pk'))
        context['categories'] = current_category
        context['item'] = self.get_random(current_category)
        # почему большие буквы???
        context['title'] = f'Тест по категории {current_category.name}'
        return context

    @staticmethod
    def get_random(category):
        max_id = Question.objects.filter(subject=category).aggregate(max_id=Max("id"))['max_id']
        while True:
            pk = randint(1, max_id)
            question = Question.objects.get(pk=pk)
            if question.available and question.subject == category:
                return question


def answers(request, id, guessed=False):
    if request.method == "POST":
        chosen_answer = list(request.POST.values())[1]
        item = Question.objects.get(id=id)
        posts = Post.objects.filter(tag=item.tag)[:4]
        user = request.user
        if chosen_answer == item.right_answer:
            guessed = True
            user.score += 1
        else:
            if user.score > 0:
                user.score -= 1
        user.save()
        context = {
            'item': item,
            'chosen_answer': chosen_answer,
            'guessed': guessed,
            'user': user,
            'posts': posts,
        }
        return render(request, 'questions/answers.html', context)
    return render(request, 'questions/answers.html')
