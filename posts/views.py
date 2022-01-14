from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from posts.models import Post


class PostsView(ListView):
    model = Post
    template_name = 'posts/all.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Посты'
        context['posts'] = Post.objects.all()
        return context


class PostView(ListView):
    model = Post
    template_name = 'posts/read.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        post = get_object_or_404(Post, pk=self.kwargs.get('pk'))
        context['title'] = post.title
        context['post'] = post
        return context
