from django.urls import path

from .views import register, login, profile, logout, UserEdit

app_name = 'users'
urlpatterns = [
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('profile/', profile, name='profile'),
    path('logout/', logout, name='logout'),
    path('profile_edit/', UserEdit.as_view(), name='profile_edit'),
]
