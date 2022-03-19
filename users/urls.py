from django.urls import path, reverse_lazy

from .views import UserLoginView, RegisterView, UserLogoutView, UserEdit, UserImgEdit, \
    UserPostCreateView, UserQuestionCreateView, TopUsers, ProfileView, Verify, \
    FailedAuthenticationView, WriteToAdmin, UserPasswordResetView, MyPasswordResetCompleteView, \
    MyPasswordResetConfirmView, GiveMeMyButtons

app_name = 'users'
urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),

    path('register/', RegisterView.as_view(), name='register'),
    path('verify/<str:email>/<str:activation_key>/', Verify.as_view(), name='verify'),
    path('attempt_failed/<str:error>', FailedAuthenticationView.as_view(), name='failed'),

    path('password_reset/', UserPasswordResetView.as_view(), name='password_reset'),
    path('password_reset_confirm/<uidb64>/<token>/', MyPasswordResetConfirmView.as_view(success_url=reverse_lazy(
        'users:password_reset_complete')), name='password_reset_confirm'),
    path('reset/done/', MyPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile_edit/', UserEdit.as_view(), name='profile_edit'),
    path('profile_img_edit/', UserImgEdit.as_view(), name='profile_img_edit'),
    path('profile_buttons/', GiveMeMyButtons.as_view(), name='give_me_my_buttons'),

    path('posts_create/', UserPostCreateView.as_view(), name='user_post_create'),
    path('question_create/', UserQuestionCreateView.as_view(), name='user_question_create'),
    path('top_users/', TopUsers.as_view(), name='top_users'),
    path('write_to_admin/', WriteToAdmin.as_view(), name='write_to_admin'),
]
