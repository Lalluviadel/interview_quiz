from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from interview_quiz.mixin import TitleMixin
from posts.models import Post


class PostsView(ListView, TitleMixin):
    model = Post
    template_name = 'posts/all.html'
    context_object_name = 'posts'
    title = 'Посты'

    def get_queryset(self):
        return Post.objects.filter(available=True)


class PostView(ListView):
    model = Post
    template_name = 'posts/read.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        post = get_object_or_404(Post, pk=self.kwargs.get('pk'))
        context['title'] = post.title
        context['post'] = post
        return context
