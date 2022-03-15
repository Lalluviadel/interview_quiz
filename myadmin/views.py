from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from interview_quiz.mixin import TitleMixin, UserDispatchMixin
from myadmin.forms import UserAdminRegisterForm, UserAdminProfileForm, CategoryForm, QuestionForm, PostForm
from posts.models import Post
from questions.models import QuestionCategory, Question
from users.models import MyUser


def index(request):
    context = {
        'title': 'Админка',
    }
    return render(request, 'myadmin/admin.html', context)


class UserListView(ListView, TitleMixin, UserDispatchMixin):
    model = MyUser
    template_name = 'myadmin/users/users-viewing.html'
    context_object_name = 'users'
    title = 'Просмотр пользователей'
    paginate_by = 3


class UserCreateView(CreateView, TitleMixin, UserDispatchMixin):
    model = MyUser
    template_name = 'myadmin/users/users-creating.html'
    form_class = UserAdminRegisterForm
    success_url = reverse_lazy('myadmin:admins_users')
    title = 'Добавить пользователя'


class UserUpdateView(UpdateView, TitleMixin, UserDispatchMixin):
    model = MyUser
    template_name = 'myadmin/users/users-update.html'
    form_class = UserAdminProfileForm
    success_url = reverse_lazy('myadmin:admins_users')
    title = 'Изменить пользователя'


class UserDeleteView(DeleteView, UserDispatchMixin):
    model = MyUser
    template_name = 'myadmin/users/users-update.html'
    success_url = reverse_lazy('myadmin:admins_users')

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, flag='false', *args, **kwargs):
        # что из этого лучше - можно поковырять
        # self.object = MyUser.objects.get(pk=self.kwargs['pk'])
        self.object = self.get_object()
        if 'flag' in request.POST:
            flag = request.POST['flag']
        if request.user.id != kwargs['pk']:
            if flag == 'false':
                self.object.is_active = False if self.object.is_active is True else True
                self.object.save()
            else:
                self.object.delete()

    def post(self, request, *args, **kwargs):
        self.delete(request, *args, **kwargs)
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            uuids = request.POST.getlist('elements[]')

            page_obj = MyUser.objects.filter(id__in=uuids)
            context = {'page_obj': page_obj}

            result = render_to_string('myadmin/includes/table-users.html', request=request, context=context)
            return JsonResponse({'result': result})
        return HttpResponseRedirect(self.get_success_url())


def user_is_staff(request, pk):
    user = get_object_or_404(MyUser, pk=pk)
    if request.user.id != pk:
        user.is_staff = False if user.is_staff is True else True
        user.save()

    uuids = request.POST.getlist('elements[]')

    page_obj = MyUser.objects.filter(id__in=uuids)
    context = {'page_obj': page_obj}

    result = render_to_string('myadmin/includes/table-users.html', request=request, context=context)
    return JsonResponse({'result': result})


class CategoriesListView(ListView, TitleMixin, UserDispatchMixin):
    model = QuestionCategory
    template_name = 'myadmin/categories/category-viewing.html'
    context_object_name = 'categories'
    title = 'Просмотр категорий'
    paginate_by = 2

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['objects']: QuestionCategory.objects.all().select_related()
        return context


class CategoriesUpdateView(UpdateView, TitleMixin, UserDispatchMixin):
    model = QuestionCategory
    template_name = 'myadmin/categories/category-update.html'
    form_class = CategoryForm
    success_url = reverse_lazy('myadmin:admins_categories')
    title = 'Изменить категорию'


class CategoriesCreateView(CreateView, TitleMixin, UserDispatchMixin):
    model = QuestionCategory
    template_name = 'myadmin/categories/category-creating.html'
    form_class = CategoryForm
    success_url = reverse_lazy('myadmin:admins_categories')
    title = 'Добавить категорию'


class CategoriesDeleteView(DeleteView, UserDispatchMixin):
    model = QuestionCategory
    template_name = 'myadmin/categories/category-update.html'
    success_url = reverse_lazy('myadmin:admins_categories')

    def delete(self, request, flag='false', *args, **kwargs):
        self.object = self.get_object()

        if 'flag' in request.POST:
            flag = request.POST['flag']
        if flag == 'false':
            if self.object.available is True:
                self.object.question_set.update(available=False)
                self.object.post_set.update(available=False)
                self.object.available = False
            else:
                self.object.question_set.update(available=True)
                self.object.post_set.update(available=True)
                self.object.available = True
            self.object.save()
        else:
            self.object.delete()

    def post(self, request, *args, **kwargs):
        self.delete(request, *args, **kwargs)
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            str_to_int = list(map(int, request.POST.getlist('elements[]')))

            page_obj = QuestionCategory.objects.filter(id__in=str_to_int)
            context = {'page_obj': page_obj}

            result = render_to_string('myadmin/includes/table-categories.html', request=request, context=context)
            return JsonResponse({'result': result})
        return HttpResponseRedirect(self.get_success_url())


class QuestionListView(ListView, TitleMixin, UserDispatchMixin):
    model = Question
    template_name = 'myadmin/questions/question-viewing.html'
    context_object_name = 'questions'
    title = 'Просмотр вопросов'
    paginate_by = 3

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        # ###????
        context['questions']: Question.objects.all().select_related()
        return context


class QuestionCreateView(CreateView, TitleMixin, UserDispatchMixin):
    model = Question
    template_name = 'myadmin/questions/question-creating.html'
    form_class = QuestionForm
    success_url = reverse_lazy('myadmin:admins_questions')
    title = 'Добавить вопрос'


class QuestionUpdateView(UpdateView, TitleMixin, UserDispatchMixin):
    model = Question
    template_name = 'myadmin/questions/question-update.html'
    form_class = QuestionForm
    success_url = reverse_lazy('myadmin:admins_questions')
    title = 'Изменить вопрос'


class QuestionDeleteView(DeleteView, UserDispatchMixin):
    model = Question
    template_name = 'myadmin/questions/question-update.html'
    success_url = reverse_lazy('myadmin:admins_questions')

    def delete(self, request, flag='false', *args, **kwargs):
        self.object = self.get_object()
        if 'flag' in request.POST:
            flag = request.POST['flag']
        if flag == 'false':
            self.object.available = False if self.object.available is True else True
            self.object.save()
        else:
            self.object.delete()

    def post(self, request, *args, **kwargs):
        self.delete(request, *args, **kwargs)
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            str_to_int = list(map(int, request.POST.getlist('elements[]')))

            page_obj = Question.objects.filter(id__in=str_to_int)
            context = {'page_obj': page_obj}
            result = render_to_string('myadmin/includes/table-questions.html', request=request, context=context)
            return JsonResponse({'result': result})
        return HttpResponseRedirect(self.get_success_url())


class PostListView(ListView, TitleMixin, UserDispatchMixin):
    model = Post
    template_name = 'myadmin/posts/post-viewing.html'
    context_object_name = 'posts'
    title = 'Просмотр статей'
    paginate_by = 3

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.all().select_related()
        return context


class PostCreateView(CreateView, TitleMixin, UserDispatchMixin):
    model = Post
    template_name = 'myadmin/posts/post-creating.html'
    form_class = PostForm
    success_url = reverse_lazy('myadmin:admins_posts')
    title = 'Добавить статью'


class PostUpdateView(UpdateView, TitleMixin, UserDispatchMixin):
    model = Post
    template_name = 'myadmin/posts/post-update.html'
    form_class = PostForm
    success_url = reverse_lazy('myadmin:admins_posts')
    title = 'Изменить статью'


class PostDeleteView(DeleteView, UserDispatchMixin):
    model = Post
    template_name = 'myadmin/posts/post-update.html'
    success_url = reverse_lazy('myadmin:admins_posts')

    def delete(self, request, flag='false', *args, **kwargs):
        self.object = self.get_object()
        if 'flag' in request.POST:
            flag = request.POST['flag']
        if flag == 'false':
            self.object.available = False if self.object.available is True else True
            self.object.save()
        else:
            self.object.delete()

    def post(self, request, *args, **kwargs):
        self.delete(request, *args, **kwargs)
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            str_to_int = list(map(int, request.POST.getlist('elements[]')))
            page_obj = Post.objects.filter(id__in=str_to_int)
            context = {'page_obj': page_obj}
            result = render_to_string('myadmin/includes/table-posts.html', request=request, context=context)
            return JsonResponse({'result': result})
        return HttpResponseRedirect(self.get_success_url())
