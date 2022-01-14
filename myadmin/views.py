from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from myadmin.forms import UserAdminRegisterForm, UserAdminProfileForm, CategoryForm, QuestionForm, PostForm
from posts.models import Post
from questions.models import QuestionCategory, Question
from users.models import MyUser


def index(request):
    context = {
        'title': 'Админка',
    }
    return render(request, 'myadmin/admin.html', context)


class UserListView(ListView):  # , CustomDispatchMixin):
    model = MyUser
    template_name = 'myadmin/users/users-viewing.html'
    context_object_name = 'users'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Просмотр пользователей'
        return context


class UserCreateView(CreateView):
    model = MyUser
    template_name = 'myadmin/users/users-creating.html'
    form_class = UserAdminRegisterForm
    success_url = reverse_lazy('myadmin:admins_users')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить пользователя'
        return context


class UserUpdateView(UpdateView):
    model = MyUser
    template_name = 'myadmin/users/users-update.html'
    form_class = UserAdminProfileForm
    success_url = reverse_lazy('myadmin:admins_users')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Изменить пользователя'
        return context


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


class CategoriesListView(ListView):
    model = QuestionCategory
    template_name = 'myadmin/categories/category-viewing.html'
    context_object_name = 'categories'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Просмотр категорий'
        context['objects']: QuestionCategory.objects.all().select_related()
        return context


class CategoriesUpdateView(UpdateView):
    model = QuestionCategory
    template_name = 'myadmin/categories/category-update.html'
    form_class = CategoryForm
    success_url = reverse_lazy('myadmin:admins_categories')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Изменить категорию'
        return context


class CategoriesCreateView(CreateView):
    model = QuestionCategory
    template_name = 'myadmin/categories/category-creating.html'
    form_class = CategoryForm
    success_url = reverse_lazy('myadmin:admins_categories')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить категорию'
        return context


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


class QuestionListView(ListView):
    model = Question
    template_name = 'myadmin/questions/question-viewing.html'
    context_object_name = 'questions'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Просмотр вопросов'
        context['questions']: Question.objects.all().select_related()
        return context


class QuestionCreateView(CreateView):
    model = Question
    template_name = 'myadmin/questions/question-creating.html'
    form_class = QuestionForm
    success_url = reverse_lazy('myadmin:admins_questions')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить вопрос'
        return context


class QuestionUpdateView(UpdateView):
    model = Question
    template_name = 'myadmin/questions/question-update.html'
    form_class = QuestionForm
    success_url = reverse_lazy('myadmin:admins_questions')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Изменить вопрос'
        return context


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


class PostListView(ListView):
    model = Post
    template_name = 'myadmin/posts/post-viewing.html'
    context_object_name = 'posts'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Просмотр статей'
        context['posts'] = Post.objects.all().select_related()
        return context


class PostCreateView(CreateView):
    model = Post
    template_name = 'myadmin/posts/post-creating.html'
    form_class = PostForm
    success_url = reverse_lazy('myadmin:admins_posts')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить статью'
        return context


class PostUpdateView(UpdateView):
    model = Post
    template_name = 'myadmin/posts/post-update.html'
    form_class = PostForm
    success_url = reverse_lazy('myadmin:admins_posts')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Изменить статью'
        return context


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
