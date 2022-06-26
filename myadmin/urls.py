from django.urls import path

from .views import AdminPanelView, UserListView, UserUpdateView, UserDeleteView, \
    UserCreateView, CategoriesListView, CategoriesUpdateView, \
    CategoriesCreateView, CategoriesDeleteView, QuestionListView, QuestionCreateView, QuestionUpdateView, \
    QuestionDeleteView, PostListView, PostCreateView, PostUpdateView, PostDeleteView, UserIsStaff, \
    AdminsSearchQuestionView, AdminsSearchPostView, AdminsSearchUserView, AdminsSearchCategoryView

app_name = 'myadmin'
urlpatterns = [
    path('', AdminPanelView.as_view(), name='admins_index'),
    path('users/', UserListView.as_view(), name='admins_users'),
    path('users-create/', UserCreateView.as_view(), name='admins_user_create'),
    path('users-update/<uuid:pk>/', UserUpdateView.as_view(), name='admins_user_update'),
    path('users-delete/<uuid:pk>/', UserDeleteView.as_view(), name='admins_user_delete'),

    path('users-is-staff/<uuid:pk>/', UserIsStaff.as_view(), name='admins_user_is_staff'),

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

    path('search/user/', AdminsSearchUserView.as_view(), name='admins_search_results_user'),
    path('search/cat/', AdminsSearchCategoryView.as_view(), name='admins_search_results_category'),
    path('search/question/', AdminsSearchQuestionView.as_view(), name='admins_search_results_question'),
    path('search/post/', AdminsSearchPostView.as_view(), name='admins_search_results_post'),
]
