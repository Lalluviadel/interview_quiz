from django.urls import path

from .views import PostView, PostsView

app_name = 'posts'
urlpatterns = [
    path('all/', PostsView.as_view(), name='all'),
    path('post/<int:pk>/', PostView.as_view(), name='post'),
]
