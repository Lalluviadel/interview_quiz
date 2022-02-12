from django.urls import path

from .views import register, login, logout, UserEdit, UserImgEdit, \
    UserPostCreateView, UserQuestionCreateView, TopUsers, profile, verify, failed_attempt

app_name = 'users'
urlpatterns = [
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('profile/', profile, name='profile'),
    path('logout/', logout, name='logout'),

    path('profile_edit/', UserEdit.as_view(), name='profile_edit'),
    path('profile_img_edit/', UserImgEdit.as_view(), name='profile_img_edit'),

    path('posts_create/', UserPostCreateView.as_view(), name='user_post_create'),
    path('question_create/', UserQuestionCreateView.as_view(), name='user_question_create'),
    path('top_users/', TopUsers.as_view(), name='top_users'),

    path('verify/<str:email>/<str:activation_key>/', verify, name='verify'),

    path('attempt_failed/<str:error>', failed_attempt, name='failed'),
]
