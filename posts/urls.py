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
