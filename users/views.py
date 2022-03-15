from django.contrib import auth, messages
from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetCompleteView
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import UpdateView, CreateView, ListView

from interview_quiz.mixin import UserDispatchMixin, TitleMixin
from interview_quiz.settings import DOMAIN_NAME, EMAIL_HOST_USER
from myadmin.forms import PostForm, QuestionForm
from posts.models import Post
from questions.models import QuestionCategory, Question
from users.forms import UserLoginForm, UserRegisterForm, UserProfileForm, UserChangeProfileForm, \
    UserImgChangeProfileForm, WriteAdminForm, MyPasswordResetForm
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
    return render(request, 'registration/login.html', context)


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
    return render(request, 'registration/register.html', context)


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
            return render(request, 'registration/verification.html')
    except TypeError:
        msg = 'Сбой активации. Попробуйте использовать ссылку, полученную в письме, повторно'
        return HttpResponseRedirect(reverse('users:failed', kwargs={'error': msg}))


def send_verify_link(user):
    """Send to user an email with verification link"""
    verify_link = reverse('users:verify', args=[user.email, user.activation_key])
    subject = f"Подтверждение регистрации на сайте {DOMAIN_NAME}"
    context = {
        'my_user': user.username,
        'my_site_name': DOMAIN_NAME,
        'my_link': f'{DOMAIN_NAME}{verify_link}',
    }
    message = render_to_string('registration/activation_msg.html', context)
    return send_mail(subject, message, EMAIL_HOST_USER, [user.email],
                     html_message=message, fail_silently=False)


def failed_attempt(request, error):
    """If activation user's profile or VK-authentication is failed, the user will be redirected with an error message"""
    context = {
        'title': 'Interview challenge',
        'error': error,
    }
    return render(request, 'registration/attempt_failed.html', context)


def write_to_admin(request):
    user = request.user.username
    email = request.user.email

    if request.method == 'POST':
        form = WriteAdminForm(request.POST)
        if form.is_valid():
            try:
                subject = f"Пользователь {user} написал вам сообщение"
                context = {
                    'user': user,
                    'my_site_name': DOMAIN_NAME,
                    'title': request.POST['title'],
                    'content': request.POST['content'],
                    'grade': request.POST['grade'],
                    'email': email,
                }
                message = render_to_string('emails/new_email.html', context)
                send_mail(subject, message, EMAIL_HOST_USER, [EMAIL_HOST_USER],
                          html_message=message, fail_silently=False)
                return redirect(reverse_lazy('users:profile'))
            except Exception:
                form.add_error(None, 'Ошибка отправки сообщения')
    else:
        form = WriteAdminForm()

    context = {
        'title': 'Написать письмо',
        'form': form,
        'user': user,
        'email': email,
    }
    return render(request, 'user_activities/write_to_admin.html', context)


def password_reset(request):
    if request.method == 'POST':
        form = MyPasswordResetForm(data=request.POST)
        if form.is_valid():
            email = request.POST['email']
            context = {
                'email': email,
                'domain': DOMAIN_NAME,
            }
            form.save(DOMAIN_NAME, subject_template_name='registration/pass_reset_subject.txt',
                      email_template_name='registration/pass_reset_email.html',
                      from_email=EMAIL_HOST_USER, extra_email_context=context)

            return render(request, 'registration/password_reset_email_sended.html')

    else:
        form = MyPasswordResetForm()
    context = {
        'title': 'Восстановление пароля',
        'form': form,
    }
    return render(request, 'registration/password_reset.html', context)


class MyPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_res_confirm.html'
    title = 'Создание нового пароля'


class MyPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/password_res_complete.html'
    title = 'Пароль успешно изменен'

def give_me_my_buttons(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        result = render_to_string('includes/profile_buttons.html', request=request)
        return JsonResponse({'result': result})
