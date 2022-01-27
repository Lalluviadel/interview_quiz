from django.contrib import auth, messages
from django.http import JsonResponse
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import UpdateView

from interview_quiz.mixin import UserDispatchMixin
from users.forms import UserLoginForm, UserRegisterForm, UserProfileForm, UserChangeProfileForm
from users.models import MyUser


def login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)
            if user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('index'))
    else:
        form = UserLoginForm()
    context = {
        'title': 'Авторизация',
        'form': form,
    }
    return render(request, 'users/login.html', context)


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Вы успешно зарегистрировались')
            return HttpResponseRedirect(reverse('users:login'))
    else:
        form = UserRegisterForm()
    context = {
        'title': 'Регистрация',
        'form': form,
    }
    return render(request, 'users/register.html', context)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('index'))


def profile(request):
    context = {
        'title': 'Мой профиль',
        'form': UserProfileForm(),
    }
    return render(request, 'users/profile.html', context)


class UserEdit(UpdateView, UserDispatchMixin):
    model = MyUser
    template_name = 'includes/profile_edit.html'
    success_url = reverse_lazy('users:profile')

    def post(self, request, *args, **kwargs):
        form = UserChangeProfileForm(data=request.POST, instance=request.user)
        if form.is_valid():
            form.save()
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            result = render_to_string('./includes/profile_data.html', request=request)
            return JsonResponse({'result': result})
        return redirect(self.success_url)

    def get(self, request, *args, **kwargs):
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            context = {'form': UserChangeProfileForm(instance=request.user)}
            result = render_to_string('./includes/profile_edit.html', request=request, context=context)
            return JsonResponse({'result': result})
