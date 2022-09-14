"""Sets associations of posts application urls with their views.

Attributes:

    * app_name (str): the name of a specific web application used in different parts of the overall structure.
    * urlpatterns(list): a list of paths that determine the behavior of a web application
                         when using the urls specified in the list.
"""
from django.urls import path

from .views import PostView, PostsCategoryView, UserPostView, TagPostView, CategoryPostView, SearchPostView

app_name = 'posts'
urlpatterns = [
    path('all/', PostsCategoryView.as_view(), name='all'),
    path('post/<int:pk>/', PostView.as_view(), name='post'),
    path('user_posts/<uuid:pk>/', UserPostView.as_view(), name='user_posts'),
    path('tag_posts/<str:tag>/', TagPostView.as_view(), name='tag_posts'),
    path('category_posts/<int:pk>/', CategoryPostView.as_view(), name='category_posts'),

    path('search/', SearchPostView.as_view(), name='search_results_post'),
]
