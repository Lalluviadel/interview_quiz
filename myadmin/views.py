"""The submodule contains views for convenient and correct work with all the main entities of the
project within the admin panel.

There are views:

    * for standard work with objects according to the CRUD principle;
    * for searching for users, posts, categories and questions by a given mask (word or part of a word);
    * to grant or remove administrator rights to a user;

To reduce code duplication, two parent classes are used.
"""

from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView

from interview_quiz.mixin import TitleMixin, UserDispatchMixin
from myadmin.forms import UserAdminRegisterForm, UserAdminProfileForm, CategoryForm, QuestionForm, PostForm
from posts.models import Post
from questions.models import QuestionCategory, Question
from users.models import MyUser


class BaseListView(ListView, TitleMixin, UserDispatchMixin):
    """Parent class for QuestionListView and PostListView, required to comply with the DRY pattern."""

    def get_context_data(self, *, object_list=None, **kwargs):
        """Provides getting and saving the current category selected by the user.
        The current category is saved in the session.
        When all categories are selected (no filter), the current category in the session is reset to zero.
        """
        context = super().get_context_data(**kwargs)
        context['categories'] = QuestionCategory.objects.all()
        if self.request.GET.get('filter'):
            if self.request.GET.get('filter') == 'all':
                self.request.session['current_category'] = None
                return context
            context['current_category'] = QuestionCategory.objects.get(id=self.request.GET.get('filter')).name
            self.request.session['current_category'] = context['current_category']
        elif 'current_category' in self.request.session:
            context['current_category'] = self.request.session['current_category']
        return context


class BaseDeleteView(DeleteView, UserDispatchMixin):
    """Parent class for QuestionDeleteView and PostDeleteView, required to comply with the DRY pattern."""

    def delete(self, request, flag='false', *args, **kwargs):
        """Performs complete deletion or activation/deactivation of the object
        in accordance with the specified mode of action.

        Args:
            * request: standard parameter.
            * flag(str, optional): the default value is 'false'. A switch parameter that allows you
                                 to specify the mode of deleting an object: completely deleting an
                                 entry from the database or marking the object as inactive.
            * ``*args``: standard parameter.
            * ``**kwargs``: standard parameter.
        """
        item = self.get_object()
        if 'flag' in request.POST:
            flag = request.POST['flag']
        if flag == 'false':
            item.available = False if item.available is True else True
            item.save()
        else:
            item.delete()


class AdminPanelView(TemplateView, TitleMixin, UserDispatchMixin):
    """View for the main admin page."""
    template_name = 'myadmin/admin.html'
    title = 'Админка'


class UserListView(ListView, TitleMixin, UserDispatchMixin):
    """View to view lists of all registered users of the site in the admin panel."""
    model = MyUser
    template_name = 'myadmin/users/users-viewing.html'
    context_object_name = 'users'
    title = 'Просмотр пользователей'
    paginate_by = 3


class UserCreateView(CreateView, TitleMixin, UserDispatchMixin):
    """View to create a new user in the admin panel."""
    model = MyUser
    template_name = 'myadmin/users/users-creating.html'
    form_class = UserAdminRegisterForm
    success_url = reverse_lazy('myadmin:admins_users')
    title = 'Добавить пользователя'


class UserUpdateView(UpdateView, TitleMixin, UserDispatchMixin):
    """View to update a specific user in the admin panel."""
    model = MyUser
    template_name = 'myadmin/users/users-update.html'
    form_class = UserAdminProfileForm
    success_url = reverse_lazy('myadmin:admins_users')
    title = 'Изменить пользователя'


class UserDeleteView(DeleteView, UserDispatchMixin):
    """View to delete or activate/deactivate a specific user in the admin panel."""
    model = MyUser
    template_name = 'myadmin/users/users-update.html'
    success_url = reverse_lazy('myadmin:admins_users')

    def delete(self, request, flag='false', *args, **kwargs):
        """Performs complete deletion or activation/deactivation of the user
        in accordance with the specified mode of action.

        Args:
            * request: standard parameter.
            * flag(str, optional): the default value is 'false'. A switch parameter that allows you
                                 to specify the mode of deleting an object: completely deleting an
                                 entry from the database or marking the object as inactive.
            * ``*args``: standard parameter.
            * ``**kwargs``: standard parameter.
        """
        item = self.get_object()
        if 'flag' in request.POST:
            flag = request.POST['flag']
        if request.user.id != kwargs['pk']:
            if flag == 'false':
                item.is_active = False if item.is_active is True else True
                item.save()
            else:
                item.delete()

    def post(self, request, *args, **kwargs):
        """Starts the process of deleting or activating/deactivating user.
        When enabled ajax, returns data for an asynchronous web request"""
        self.delete(request, *args, **kwargs)
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            uuids = request.POST.getlist('elements[]')

            page_obj = MyUser.objects.filter(id__in=uuids)
            context = {'page_obj': page_obj}

            result = render_to_string('myadmin/includes/table-users.html', request=request, context=context)
            return JsonResponse({'result': result})
        return render(request, 'myadmin/users/users-viewing.html')


class UserIsStaff(UpdateView, UserDispatchMixin):
    """View for granting the user rights/removing the rights of the superuser in the admin panel."""
    model = MyUser
    form_class = UserAdminProfileForm
    template_name = 'myadmin/includes/table-users.html'

    def post(self, request, *args, **kwargs):
        """Sets superuser rights for the selected user or deletes them.
        When enabled ajax, returns data for an asynchronous web request."""
        user = get_object_or_404(MyUser, pk=kwargs['pk'])
        if self.request.user != user:
            user.is_staff = False if user.is_staff is True else True
            user.save()
        uuids = request.POST.getlist('elements[]')
        page_obj = MyUser.objects.filter(id__in=uuids)
        context = {'page_obj': page_obj}
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            result = render_to_string('myadmin/includes/table-users.html', request=request, context=context)
            return JsonResponse({'result': result})
        return render(request, 'myadmin/users/users-viewing.html', context=context)


class CategoriesListView(ListView, TitleMixin, UserDispatchMixin):
    """View to view list of all categories of the site in the admin panel."""
    model = QuestionCategory
    template_name = 'myadmin/categories/category-viewing.html'
    context_object_name = 'categories'
    title = 'Просмотр категорий'
    paginate_by = 2

    def get_context_data(self, *, object_list=None, **kwargs):
        """Overrides the method of the parent class to optimize the query."""
        context = super().get_context_data(**kwargs)
        context['objects']: QuestionCategory.objects.all().select_related()
        return context


class CategoriesCreateView(CreateView, TitleMixin, UserDispatchMixin):
    """View to create a new category in the admin panel."""
    model = QuestionCategory
    template_name = 'myadmin/categories/category-creating.html'
    form_class = CategoryForm
    success_url = reverse_lazy('myadmin:admins_categories')
    title = 'Добавить категорию'


class CategoriesUpdateView(UpdateView, TitleMixin, UserDispatchMixin):
    """View to update a specific category in the admin panel."""
    model = QuestionCategory
    template_name = 'myadmin/categories/category-update.html'
    form_class = CategoryForm
    success_url = reverse_lazy('myadmin:admins_categories')
    title = 'Изменить категорию'


class CategoriesDeleteView(DeleteView, UserDispatchMixin):
    """View to delete or activate/deactivate a specific category in the admin panel."""
    model = QuestionCategory
    template_name = 'myadmin/categories/category-update.html'
    success_url = reverse_lazy('myadmin:admins_categories')

    def delete(self, request, flag='false', *args, **kwargs):
        """Performs complete deletion or activation/deactivation of the category
        in accordance with the specified mode of action.
        At the same time, all posts and questions in this category also become active/inactive.

        Args:
            * request: standard parameter.
            * flag(str, optional): the default value is 'false'. A switch parameter that allows you
                                 to specify the mode of deleting an object: completely deleting an
                                 entry from the database or marking the object as inactive.
            * ``*args``: standard parameter.
            * ``**kwargs``: standard parameter.
        """
        item = self.get_object()
        if 'flag' in request.POST:
            flag = request.POST['flag']
        if flag == 'false':
            if item.available is True:
                item.question_set.update(available=False)
                item.post_set.update(available=False)
                item.available = False
            else:
                item.question_set.update(available=True)
                item.post_set.update(available=True)
                item.available = True
            item.save()
        else:
            item.delete()

    def post(self, request, *args, **kwargs):
        """Starts the process of deleting or activating/deactivating category.
        When enabled ajax, returns data for an asynchronous web request.
        """
        self.delete(request, *args, **kwargs)
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            str_to_int = list(map(int, request.POST.getlist('elements[]')))

            page_obj = QuestionCategory.objects.filter(id__in=str_to_int)
            context = {'page_obj': page_obj}

            result = render_to_string('myadmin/includes/table-categories.html', request=request, context=context)
            return JsonResponse({'result': result})
        return render(request, 'myadmin/categories/category-viewing.html')


class QuestionListView(BaseListView):
    """View to view list of all questions of the site in the admin panel."""
    model = Question
    template_name = 'myadmin/questions/question-viewing.html'
    context_object_name = 'questions'
    title = 'Просмотр вопросов'
    paginate_by = 3

    def get_queryset(self, filter_val=None):
        """Returns the desired queryset, depending on whether a new custom filter was passed,
        whether it existed earlier and needs to be saved (for example, page navigation during pagination),
        whether the filter cancellation was passed.

        Args:
            * filter_val (str, optional): The filter value passed when the user selects the filter category.
                                          Defaults to None.

        Returns:
            * Queryset of filtered objects of the specified category or of all objects if there is no filter.
        """
        if self.request.GET.get('filter'):
            if self.request.GET.get('filter') == 'all':
                self.request.session['filter'] = None
                return Question.objects.select_related('subject').prefetch_related('author')
            filter_val = self.request.GET.get('filter')
            self.request.session['filter'] = filter_val
        elif 'filter' in self.request.session:
            filter_val = self.request.session['filter']
        if filter_val:
            filtered_queryset = Question.objects.filter(subject=filter_val).\
                select_related('subject').prefetch_related('author')
            return filtered_queryset
        return Question.objects.select_related('subject').prefetch_related('author')


class QuestionCreateView(CreateView, TitleMixin, UserDispatchMixin):
    """View to create a new question in the admin panel."""
    model = Question
    template_name = 'myadmin/questions/question-creating.html'
    form_class = QuestionForm
    success_url = reverse_lazy('myadmin:admins_questions')
    title = 'Добавить вопрос'

    def post(self, request, *args, **kwargs):
        """Getting the entered data of a new question,
        adding the current user as the author and saving the question.
        """
        form = self.form_class(data=request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            if request.FILES.get('image_01'):
                question.image_01 = request.FILES.get('image_01')
            if request.FILES.get('image_02'):
                question.image_02 = request.FILES.get('image_02')
            if request.FILES.get('image_03'):
                question.image_03 = request.FILES.get('image_03')
            question.author = request.user
            question.save()
            return HttpResponseRedirect(reverse('myadmin:admins_questions'))
        return render(request, self.template_name, context={'form': form})


class QuestionUpdateView(UpdateView, TitleMixin, UserDispatchMixin):
    """View to update a specific question in the admin panel."""
    model = Question
    template_name = 'myadmin/questions/question-update.html'
    form_class = QuestionForm
    success_url = reverse_lazy('myadmin:admins_questions')
    title = 'Изменить вопрос'


class QuestionDeleteView(BaseDeleteView):
    """View to delete or activate/deactivate a specific question in the admin panel."""
    model = Question
    template_name = 'myadmin/questions/question-update.html'
    success_url = reverse_lazy('myadmin:admins_questions')

    def post(self, request, *args, **kwargs):
        """Starts the process of deleting or activating/deactivating question.
        When enabled ajax, returns data for an asynchronous web request."""
        self.delete(request, *args, **kwargs)
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            str_to_int = list(map(int, request.POST.getlist('elements[]')))

            page_obj = Question.objects.filter(id__in=str_to_int)
            context = {'page_obj': page_obj}
            result = render_to_string('myadmin/includes/table-questions.html', request=request, context=context)
            return JsonResponse({'result': result})
        return render(request, 'myadmin/questions/question-viewing.html')


class PostListView(BaseListView):
    """View to view list of all posts of the site in the admin panel."""
    model = Post
    template_name = 'myadmin/posts/post-viewing.html'
    context_object_name = 'posts'
    title = 'Просмотр статей'
    paginate_by = 3

    def get_queryset(self, filter_val=None):
        """Returns the desired queryset, depending on whether a new custom filter was passed,
        whether it existed earlier and needs to be saved (for example, page navigation during pagination),
        whether the filter cancellation was passed.

        Args:
            filter_val (str, optional): The filter value passed when the user selects the filter category.
                                        Defaults to None.

        Returns:
            Queryset of filtered objects of the specified category or of all objects if there is no filter.
        """
        if self.request.GET.get('filter'):
            if self.request.GET.get('filter') == 'all':
                self.request.session['filter'] = None
                return Post.objects.select_related('category').prefetch_related('author')
            filter_val = self.request.GET.get('filter')
            self.request.session['filter'] = filter_val
        elif 'filter' in self.request.session:
            filter_val = self.request.session['filter']
        if filter_val:
            filtered_queryset = Post.objects.filter(category=filter_val).\
                select_related('category').prefetch_related('author')
            return filtered_queryset
        return Post.objects.select_related('category').prefetch_related('author')


class PostCreateView(CreateView, TitleMixin, UserDispatchMixin):
    """View to create a new post in the admin panel."""
    model = Post
    template_name = 'myadmin/posts/post-creating.html'
    form_class = PostForm
    success_url = reverse_lazy('myadmin:admins_posts')
    title = 'Добавить статью'

    def post(self, request, *args, **kwargs):
        """Getting the entered data of a new post,
        adding the current user as the author and saving the question."""
        form = self.form_class(data=request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            if request.FILES.get('image'):
                post.image = request.FILES.get('image')
            post.save()
            return HttpResponseRedirect(reverse('myadmin:admins_posts'))
        return render(request, self.template_name, context={'form': form})


class PostUpdateView(UpdateView, TitleMixin, UserDispatchMixin):
    """View to update a specific post in the admin panel."""
    model = Post
    template_name = 'myadmin/posts/post-update.html'
    form_class = PostForm
    success_url = reverse_lazy('myadmin:admins_posts')
    title = 'Изменить статью'


class PostDeleteView(BaseDeleteView):
    """View to delete or activate/deactivate a specific post in the admin panel."""
    model = Post
    template_name = 'myadmin/posts/post-update.html'
    success_url = reverse_lazy('myadmin:admins_posts')

    def post(self, request, *args, **kwargs):
        """Starts the process of deleting or activating/deactivating post.
        When enabled ajax, returns data for an asynchronous web request.
        """
        self.delete(request, *args, **kwargs)
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            str_to_int = list(map(int, request.POST.getlist('elements[]')))
            page_obj = Post.objects.filter(id__in=str_to_int)
            context = {'page_obj': page_obj}
            result = render_to_string('myadmin/includes/table-posts.html', request=request, context=context)
            return JsonResponse({'result': result})
        return render(request, 'myadmin/posts/post-viewing.html')


class AdminsSearchUserView(ListView, TitleMixin, UserDispatchMixin):
    """View to display the search results for users (when using the site search bar).
    The search is performed by username of user, first name, last name, or part of them.
    """
    model = MyUser
    template_name = 'myadmin/users/search_results_user.html'
    title = 'Поиск пользователя'

    def get_queryset(self):
        """Returns a queryset filtered for the presence of a match with the data entered by the user."""
        query = self.request.GET.get('admins_search_panel')
        if query:
            object_list = MyUser.objects.filter(Q(username__icontains=query) |
                                                Q(last_name__icontains=query) |
                                                Q(first_name__contains=query))
            return object_list
        return MyUser.objects.all()


class AdminsSearchCategoryView(ListView, TitleMixin, UserDispatchMixin):
    """View to display the search results for categories (when using the site search bar).
    The search is performed by name of category or its part.
    """
    model = QuestionCategory
    template_name = 'myadmin/categories/search_results_category.html'
    title = 'Поиск категории'

    def get_queryset(self):
        """Returns a queryset filtered for the presence of a match with the data entered by the user."""
        query = self.request.GET.get('admins_search_panel')
        if query:
            object_list = QuestionCategory.objects.filter(name__icontains=query)
            return object_list
        return QuestionCategory.objects.all()


class AdminsSearchQuestionView(ListView, TitleMixin, UserDispatchMixin):
    """View to display the search results for questions (when using the site search bar).
    The search is performed by name of question, tag, or part of them.
    """
    model = Question
    template_name = 'myadmin/questions/search_results_question.html'
    title = 'Поиск вопроса'

    def get_queryset(self):
        """Returns a queryset filtered for the presence of a match with the data entered by the user."""
        query = self.request.GET.get('admins_search_panel')
        if query:
            object_list = Question.objects.filter(Q(question__icontains=query) | Q(tag__icontains=query))
            return object_list
        return Question.objects.all()


class AdminsSearchPostView(ListView, TitleMixin, UserDispatchMixin):
    """View to display the search results for posts (when using the site search bar).
    The search is performed by title of post, tag, or part of them.
    """
    model = Post
    template_name = 'myadmin/posts/search_results_post.html'
    title = 'Поиск статьи'

    def get_queryset(self):
        """Returns a queryset filtered for the presence of a match with the data entered by the user.
        """
        query = self.request.GET.get('admins_search_panel')
        if query:
            object_list = Post.objects.filter(Q(title__icontains=query) | Q(tag__icontains=query))
            return object_list
        return Post.objects.all()
