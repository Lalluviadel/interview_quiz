from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView

from interview_quiz.mixin import TitleMixin, AuthorizedOnlyDispatchMixin
from posts.models import Post
from questions.models import QuestionCategory
from users.models import MyUser


class PostsCategoryView(ListView, TitleMixin):
    """View for displaying all posts by category (only active categories)"""
    model = QuestionCategory
    template_name = 'posts/all.html'
    context_object_name = 'posts_categories'
    title = 'Посты'

    def get_queryset(self):
        """Displaying all active categories.
        A category is displayed only if it has at least one active post.
        At the same time, the template displays the number of active posts in this category."""
        return QuestionCategory.objects.filter(available=True).\
            annotate(posts_count=Count('post', distinct=True)).filter(post__available=True)


class PostView(DetailView):
    """View for the output of a separate post"""
    model = Post
    template_name = 'posts/read.html'

    def get_context_data(self, *args, **kwargs):
        """Getting a specific post and its title and passing it to the context"""
        context = super().get_context_data(**kwargs)
        post = get_object_or_404(Post, pk=self.kwargs.get('pk'))
        context['title'] = post.title
        context['post'] = post
        return context


class UserPostView(ListView, AuthorizedOnlyDispatchMixin):
    """View for displaying posts of a specific user.
    It is triggered when you click on the author's nickname when you are
    on the page of a particular post"""
    model = Post
    template_name = 'posts/user_posts.html'

    def get_context_data(self, *args, **kwargs):
        """Retrieves a specific user and a queryset of his posts and transfers to the context"""
        context = super().get_context_data(**kwargs)
        user = MyUser.objects.get(id=self.kwargs.get('pk'))
        user_posts = Post.objects.filter(Q(author=user), Q(available=True)).defer('category', 'body',
                                                                                  'image', 'created_on', 'tag')
        context['user_posts'] = user_posts
        context['title'] = f'Посты пользователя {user}'
        context['user'] = user
        return context


class TagPostView(ListView):
    """View to display posts with a specific tag.
    It is triggered when you click on the tag when you are on the page of a certain post"""
    model = Post
    template_name = 'posts/tag_posts.html'

    def get_context_data(self, *args, **kwargs):
        """Retrieves a specific tag and a queryset of posts with this tag and passes it to the context"""
        context = super().get_context_data(**kwargs)
        tag = self.kwargs.get('tag')
        context['tag_posts'] = Post.objects.filter(Q(tag=tag), Q(available=True)).defer('author', 'category',
                                                                                        'body', 'image', 'created_on')
        context['tag'] = tag
        context['title'] = f'Посты с тегом {tag}'
        return context


class CategoryPostView(ListView):
    """View to display posts of a specific category.
    It is triggered when you click on the category when you are on the page of a certain post"""
    model = Post
    template_name = 'posts/category_posts.html'

    def get_context_data(self, *args, **kwargs):
        """Retrieves a specific category and a queryset of posts of this category and passes it to the context"""
        context = super().get_context_data(**kwargs)
        category = QuestionCategory.objects.get(id=self.kwargs.get('pk'))
        context['category_posts'] = Post.objects.filter(Q(category=category),
                                                        Q(available=True)).defer('author', 'tag', 'body',
                                                                                 'image', 'created_on')
        context['category'] = category
        context['title'] = f'Посты категории {category}'
        return context


class SearchPostView(ListView, TitleMixin):
    """View to display the search result posts.
    It is triggered when you use the search bar at the top of the page.
    The search is performed using the following options:
    - by tag;
    - by the title;
    - by the part of tag or of title;
    """
    model = Post
    template_name = 'posts/search_results_post.html'
    title = 'Поиск статьи'

    def get_queryset(self):
        """Retrieves the search mask specified by the user and
        returns a queryset of posts according to the filter by this mask"""
        query = self.request.GET.get('search_panel')
        object_list = Post.objects.filter(Q(title__icontains=query) | Q(tag__icontains=query)).\
            filter(available=True).defer('author', 'body', 'image', 'created_on', 'category')
        return object_list
