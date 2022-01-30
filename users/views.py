from django.contrib import auth, messages
from django.http import JsonResponse
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import UpdateView, CreateView, ListView

from interview_quiz.mixin import UserDispatchMixin, TitleMixin
from myadmin.forms import PostForm, QuestionForm
from posts.models import Post
from questions.models import QuestionCategory, Question
from users.forms import UserLoginForm, UserRegisterForm, UserProfileForm, UserChangeProfileForm, \
    UserImgChangeProfileForm
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
    user = MyUser.objects.get(id=request.user.id)
    index = MyUser.objects.order_by('-score').filter(score__gte=user.score).count()
    context = {
        'title': 'Мой профиль',
        'form': UserProfileForm(),
        'index': index
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


class UserImgEdit(UpdateView, UserDispatchMixin):
    model = MyUser
    template_name = 'includes/profile_img_edit.html'
    success_url = reverse_lazy('users:profile')

    def post(self, request, *args, **kwargs):
        user = MyUser.objects.get(id=request.user.id)
        user.img = request.FILES.get('image')
        user.save()
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            context = {'user': user}
            result = render_to_string('./includes/profile_img.html', request=request, context=context)
            return JsonResponse({'result': result})
        return redirect(self.success_url)

    def get(self, request, *args, **kwargs):
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            context = {'form': UserImgChangeProfileForm(instance=request.user)}
            result = render_to_string('./includes/profile_img_edit.html', request=request, context=context)
            return JsonResponse({'result': result})


class UserPostCreateView(CreateView, TitleMixin):
    model = Post
    template_name = 'user_activities/add_post.html'
    form_class = PostForm
    success_url = reverse_lazy('users:profile')
    title = 'Написать свою статью'

    def post(self, request, *args, **kwargs):
        category = QuestionCategory.objects.get(id=request.POST['category'])
        image = request.FILES.get('image')
        title, tag, body = request.POST['title'], request.POST['tag'], request.POST['body']
        Post.objects.create(author=request.user, title=title, tag=tag,
                            category=category, image=image, body=body)
        return redirect(self.success_url)


class UserQuestionCreateView(CreateView, TitleMixin):
    model = Question
    template_name = 'user_activities/add_question.html'
    form_class = QuestionForm
    success_url = reverse_lazy('users:profile')
    title = 'Предложить свой вопрос'


class TopUsers(ListView, TitleMixin):
    model = MyUser
    template_name = 'user_activities/top_users.html'
    title = 'Топ-5 участников'
    context_object_name = 'top_users'

    def get_queryset(self):
        return MyUser.objects.order_by('-score')[:5]
