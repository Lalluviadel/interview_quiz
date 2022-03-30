from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView

from interview_quiz.mixin import TitleMixin, AuthorizedOnlyDispatchMixin
from posts.models import Post
from questions.models import QuestionCategory
from users.models import MyUser


class PostsCategoryView(ListView, TitleMixin):
    model = QuestionCategory
    template_name = 'posts/all.html'
    context_object_name = 'posts_categories'
    title = 'Посты'

    def get_queryset(self):
        return QuestionCategory.objects.filter(available=True)


class PostView(DetailView):
    model = Post
    template_name = 'posts/read.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        post = get_object_or_404(Post, pk=self.kwargs.get('pk'))
        context['title'] = post.title
        context['post'] = post
        return context


class UserPostView(ListView, AuthorizedOnlyDispatchMixin):
    model = Post
    template_name = 'posts/user_posts.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        user = MyUser.objects.get(id=self.kwargs.get('pk'))
        user_posts = Post.objects.filter(Q(author=user), Q(available=True)).defer('category', 'body',
                                                                                  'image', 'created_on', 'tag')
        context['user_posts'] = user_posts
        context['title'] = f'Посты пользователя {user}'
        context['user'] = user
        return context


class TagPostView(ListView):
    model = Post
    template_name = 'posts/tag_posts.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = self.kwargs.get('tag')
        context['tag_posts'] = Post.objects.filter(Q(tag=tag), Q(available=True)).defer('author', 'category',
                                                                                        'body', 'image', 'created_on')
        context['tag'] = tag
        context['title'] = f'Посты с тегом {tag}'
        return context


class CategoryPostView(ListView):
    model = Post
    template_name = 'posts/category_posts.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        category = QuestionCategory.objects.get(id=self.kwargs.get('pk'))
        context['category_posts'] = Post.objects.filter(Q(category=category),
                                                        Q(available=True)).defer('author', 'tag', 'body',
                                                                                 'image', 'created_on')
        context['category'] = category
        context['title'] = f'Посты категории {category}'
        return context


class SearchPostView(ListView, TitleMixin):
    model = Post
    template_name = 'posts/search_results_post.html'
    title = 'Поиск статьи'

    def get_queryset(self):
        query = self.request.GET.get('search_panel')
        object_list = Post.objects.filter(Q(title__icontains=query) | Q(tag__icontains=query)).defer('author', 'body',
                                                                                 'image', 'created_on', 'category')
        return object_list
