from django.contrib import auth, messages
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import UpdateView, CreateView, ListView

from interview_quiz import settings
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
            user = form.save()
            if send_verify_link(user):
                messages.success(request, 'Для завершения регистрации используйте ссылку из письма, отправленного '
                                          'на email, указанный при регистрации.')
            return HttpResponseRedirect(reverse('users:register'))

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
    """Creating a new post by a user"""
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
    """Creating a new question by a user"""
    model = Question
    template_name = 'user_activities/add_question.html'
    form_class = QuestionForm
    success_url = reverse_lazy('users:profile')
    title = 'Предложить свой вопрос'

    def post(self, request, *args, **kwargs):
        subject = QuestionCategory.objects.get(id=request.POST['subject'])
        image_01, image_02, image_03 = request.FILES.get('image_01'), request.FILES.get('image_02'),\
                                       request.FILES.get('image_03')

        right_answer, question, tag = request.POST['right_answer'], request.POST['question'], request.POST['tag']
        difficulty_level = request.POST['difficulty_level']
        answer_01, answer_02, answer_03, answer_04 = request.POST['answer_01'], request.POST['answer_02'], \
                                                     request.POST['answer_03'], request.POST['answer_04']

        Question.objects.create(author=request.user, subject=subject, tag=tag, image_01=image_01, image_02=image_02,
                                image_03=image_03, difficulty_level=difficulty_level, answer_01=answer_01,
                                answer_02=answer_02, answer_03=answer_03, answer_04=answer_04, question=question,
                                right_answer=right_answer)

        return redirect(self.success_url)


class TopUsers(ListView, TitleMixin):
    """Shows users top-5"""
    model = MyUser
    template_name = 'user_activities/top_users.html'
    title = 'Топ-5 участников'
    context_object_name = 'top_users'

    def get_queryset(self):
        return MyUser.objects.order_by('-score')[:5]


def verify(request, email, activation_key):
    """New user activation and authorization"""
    try:
        user = MyUser.objects.get(email=email)

        if user.is_activation_key_expired():
            send_verify_link(user)
            msg = 'Ваш ключ активации устарел. Мы направили на вашу почту письмо с новым ключом активации'
            return HttpResponseRedirect(reverse('users:failed', kwargs={'error': msg}))

        elif user and user.activation_key == activation_key:
            user.activation_key = ''
            user.activation_key_created = None
            user.is_active = True
            auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            user.save()
            return render(request, 'users/verification.html')
    except TypeError:
        msg = 'Сбой активации. Попробуйте использовать ссылку, полученную в письме, повторно'
        return HttpResponseRedirect(reverse('users:failed', kwargs={'error': msg}))


def send_verify_link(user):
    """Send to user an email with verification link"""
    verify_link = reverse('users:verify', args=[user.email, user.activation_key])
    subject = f"Подтверждение регистрации на сайте {settings.DOMAIN_NAME}"
    context = {
        'my_user': user.username,
        'my_site_name': settings.DOMAIN_NAME,
        'my_link': f'{settings.DOMAIN_NAME}{verify_link}',
    }
    message = render_to_string('users/activation_msg.html', context)
    return send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email],
                     html_message=message, fail_silently=False)


def failed_attempt(request, error):
    """If activation user's profile or VK-authentication is failed, the user will be redirected with an error message"""
    context = {
        'title': 'Interview challenge',
        'error': error,
    }
    return render(request, 'users/attempt_failed.html', context)
