from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from interview_quiz.mixin import TitleMixin
from myadmin.forms import UserAdminRegisterForm, UserAdminProfileForm, CategoryForm, QuestionForm, PostForm
from posts.models import Post
from questions.models import QuestionCategory, Question
from users.models import MyUser


def index(request):
    context = {
        'title': 'Админка',
    }
    return render(request, 'myadmin/admin.html', context)


class UserListView(ListView, TitleMixin):  # , CustomDispatchMixin):
    model = MyUser
    template_name = 'myadmin/users/users-viewing.html'
    context_object_name = 'users'
    title = 'Просмотр пользователей'


class UserCreateView(CreateView, TitleMixin):
    model = MyUser
    template_name = 'myadmin/users/users-creating.html'
    form_class = UserAdminRegisterForm
    success_url = reverse_lazy('myadmin:admins_users')
    title = 'Добавить пользователя'


class UserUpdateView(UpdateView, TitleMixin):
    model = MyUser
    template_name = 'myadmin/users/users-update.html'
    form_class = UserAdminProfileForm
    success_url = reverse_lazy('myadmin:admins_users')
    title = 'Изменить пользователя'


class UserDeleteView(DeleteView):
    model = MyUser
    template_name = 'myadmin/users/users-update.html'
    success_url = reverse_lazy('myadmin:admins_users')

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        # что из этого лучше - можно поковырять
        # self.object = MyUser.objects.get(pk=self.kwargs['pk'])
        self.object = self.get_object()
        if request.user.id != kwargs['pk']:
            self.object.is_active = False if self.object.is_active is True else True
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        self.delete(request, *args, **kwargs)
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            result = render_to_string('myadmin/includes/table-users.html', request=request)
            return JsonResponse({'result': result})
        return HttpResponseRedirect(self.get_success_url())


def user_is_staff(request, pk):
    user = get_object_or_404(MyUser, pk=pk)
    if request.user.id != pk:
        user.is_staff = False if user.is_staff is True else True
        user.save()
    result = render_to_string('myadmin/includes/table-users.html', request=request)
    return JsonResponse({'result': result})


class CategoriesListView(ListView, TitleMixin):
    model = QuestionCategory
    template_name = 'myadmin/categories/category-viewing.html'
    context_object_name = 'categories'
    title = 'Просмотр категорий'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['objects']: QuestionCategory.objects.all().select_related()
        return context


class CategoriesUpdateView(UpdateView, TitleMixin):
    model = QuestionCategory
    template_name = 'myadmin/categories/category-update.html'
    form_class = CategoryForm
    success_url = reverse_lazy('myadmin:admins_categories')
    title = 'Изменить категорию'


class CategoriesCreateView(CreateView, TitleMixin):
    model = QuestionCategory
    template_name = 'myadmin/categories/category-creating.html'
    form_class = CategoryForm
    success_url = reverse_lazy('myadmin:admins_categories')
    title = 'Добавить категорию'


class CategoriesDeleteView(DeleteView):
    model = QuestionCategory
    template_name = 'myadmin/categories/category-update.html'
    success_url = reverse_lazy('myadmin:admins_categories')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.available is True:
            self.object.question_set.update(available=False)
            self.object.available = False
        else:
            self.object.question_set.update(available=True)
            self.object.available = True
        self.object.save()

    def post(self, request, *args, **kwargs):
        self.delete(request, *args, **kwargs)
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            result = render_to_string('myadmin/includes/table-categories.html', request=request)
            return JsonResponse({'result': result})
        return HttpResponseRedirect(self.get_success_url())


class QuestionListView(ListView, TitleMixin):
    model = Question
    template_name = 'myadmin/questions/question-viewing.html'
    context_object_name = 'questions'
    title = 'Просмотр вопросов'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        ####????
        context['questions']: Question.objects.all().select_related()
        return context


class QuestionCreateView(CreateView, TitleMixin):
    model = Question
    template_name = 'myadmin/questions/question-creating.html'
    form_class = QuestionForm
    success_url = reverse_lazy('myadmin:admins_questions')
    title = 'Добавить вопрос'


class QuestionUpdateView(UpdateView, TitleMixin):
    model = Question
    template_name = 'myadmin/questions/question-update.html'
    form_class = QuestionForm
    success_url = reverse_lazy('myadmin:admins_questions')
    title = 'Изменить вопрос'


class QuestionDeleteView(DeleteView):
    model = Question
    template_name = 'myadmin/questions/question-update.html'
    success_url = reverse_lazy('myadmin:admins_questions')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.available = False if self.object.available is True else True
        self.object.save()

    def post(self, request, *args, **kwargs):
        self.delete(request, *args, **kwargs)
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            result = render_to_string('myadmin/includes/table-questions.html', request=request)
            return JsonResponse({'result': result})
        return HttpResponseRedirect(self.get_success_url())


class PostListView(ListView, TitleMixin):
    model = Post
    template_name = 'myadmin/posts/post-viewing.html'
    context_object_name = 'posts'
    title = 'Просмотр статей'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.all().select_related()
        return context


class PostCreateView(CreateView, TitleMixin):
    model = Post
    template_name = 'myadmin/posts/post-creating.html'
    form_class = PostForm
    success_url = reverse_lazy('myadmin:admins_posts')
    title = 'Добавить статью'


class PostUpdateView(UpdateView, TitleMixin):
    model = Post
    template_name = 'myadmin/posts/post-update.html'
    form_class = PostForm
    success_url = reverse_lazy('myadmin:admins_posts')
    title = 'Изменить статью'


class PostDeleteView(DeleteView):
    model = Post
    template_name = 'myadmin/posts/post-update.html'
    success_url = reverse_lazy('myadmin:admins_posts')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.available = False if self.object.available is True else True
        self.object.save()

    def post(self, request, *args, **kwargs):
        self.delete(request, *args, **kwargs)
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            posts = Post.objects.all()
            context = {'posts': posts}
            result = render_to_string('myadmin/includes/table-posts.html', context, request=request)
            return JsonResponse({'result': result})
        return HttpResponseRedirect(self.get_success_url())
