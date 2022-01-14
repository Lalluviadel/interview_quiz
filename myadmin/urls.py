from django.urls import path

from .views import index, UserListView, UserUpdateView, UserDeleteView, \
    UserCreateView, user_is_staff, CategoriesListView, CategoriesUpdateView, \
    CategoriesCreateView, CategoriesDeleteView, QuestionListView, QuestionCreateView, QuestionUpdateView, \
    QuestionDeleteView, PostListView, PostCreateView, PostUpdateView, PostDeleteView

app_name = 'myadmin'
urlpatterns = [
    path('', index, name='index'),
    path('users/', UserListView.as_view(), name='admins_users'),
    path('users-create/', UserCreateView.as_view(), name='admins_user_create'),
    path('users-delete/<int:pk>/', UserDeleteView.as_view(), name='admins_user_delete'),
    path('users-update/<int:pk>/', UserUpdateView.as_view(), name='admins_user_update'),
    path('users-is-staff/<int:pk>/', user_is_staff, name='admins_user_is_staff'),

    path('categories/', CategoriesListView.as_view(), name='admins_categories'),
    path('categories-create/', CategoriesCreateView.as_view(), name='admins_category_create'),
    path('categories-update/<int:pk>/', CategoriesUpdateView.as_view(), name='admins_category_update'),
    path('categories-delete/<int:pk>/', CategoriesDeleteView.as_view(), name='admins_category_delete'),

    path('questions/', QuestionListView.as_view(), name='admins_questions'),
    path('questions-create/', QuestionCreateView.as_view(), name='admins_question_create'),
    path('questions-update/<int:pk>/', QuestionUpdateView.as_view(), name='admins_question_update'),
    path('questions-delete/<int:pk>/', QuestionDeleteView.as_view(), name='admins_question_delete'),

    path('posts/', PostListView.as_view(), name='admins_posts'),
    path('posts-create/', PostCreateView.as_view(), name='admins_post_create'),
    path('posts-update/<int:pk>/', PostUpdateView.as_view(), name='admins_post_update'),
    path('posts-delete/<int:pk>/', PostDeleteView.as_view(), name='admins_post_delete'),
]
