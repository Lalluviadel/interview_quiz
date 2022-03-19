import logging

from django.contrib import auth, messages
from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetCompleteView, LoginView, LogoutView, \
    PasswordResetView
from django.core.mail import send_mail
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import UpdateView, CreateView, ListView, TemplateView, FormView

from interview_quiz.mixin import TitleMixin, AuthorizedOnlyDispatchMixin
from interview_quiz.settings import DOMAIN_NAME, EMAIL_HOST_USER
from myadmin.forms import PostForm, QuestionForm
from posts.models import Post
from questions.models import QuestionCategory, Question
from users.forms import UserLoginForm, UserRegisterForm, UserProfileForm, UserChangeProfileForm, \
    UserImgChangeProfileForm, WriteAdminForm, MyPasswordResetForm
from users.models import MyUser

logger = logging.getLogger(__name__)


class UserLoginView(LoginView, TitleMixin):
    template_name = 'registration/login.html'
    title = 'Авторизация'
    form_class = UserLoginForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
            if user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'registration/login.html', context={'form': form, })


class RegisterView(FormView, TitleMixin):
    template_name = 'registration/register.html'
    title = 'Регистрация нового пользователя'
    form_class = UserRegisterForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            user = form.save()
            if self.send_verify_link(user):
                messages.success(request, 'Для завершения регистрации используйте ссылку из письма, отправленного '
                                          'на email, указанный при регистрации.')

            else:
                msg = f'К сожалению, произошел сбой, письмо для завершения регистрации не было отослано. ' \
                      f'Для активации вашего профиля напишите письмо на адрес {EMAIL_HOST_USER}'
                messages.error(request, msg)
            return HttpResponseRedirect(reverse('users:register'))
        else:
            logger.warning('Неудачная попытка регистрации пользователя')
        return render(request, 'registration/register.html', context={'form': form, })

    @staticmethod
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


class Verify(TemplateView, TitleMixin):
    """New user activation and authorization"""
    title = 'Успешная активация профиля'

    def get(self, request, *args, **kwargs):
        try:
            user = MyUser.objects.get(email=kwargs['email'])

            if user.is_activation_key_expired():
                msg = f'Ваш ключ активации устарел. ' \
                      f'Для активации вашего профиля напишите письмо на адрес {EMAIL_HOST_USER} ' \
                      f'или зарегистрируйте новый профиль, используя другой email.'
                logger.error(f'Сбой активации нового пользователя - устаревший ключ активации')
                return HttpResponseRedirect(reverse('users:failed', kwargs={'error': msg}))

            elif user and user.activation_key == kwargs['activation_key']:
                user.activation_key, user.activation_key_created = '', None
                user.is_active = True
                auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                user.save()
                return render(request, 'registration/verification.html')

        except TypeError as e:
            logger.error(f'Сбой активации нового пользователя - {e}')
            msg = f'Сбой активации. Попробуйте использовать ссылку, полученную в письме, повторною. ' \
                  f'В случае неудачи напишите на адрес {EMAIL_HOST_USER}, указав причину обращения.'
            return HttpResponseRedirect(reverse('users:failed', kwargs={'error': msg}))


class FailedAuthenticationView(TemplateView):
    """If activation user's profile or VK-authentication is failed, the user will be redirected with an error message"""

    def get(self, request, *args, **kwargs):
        return render(request, 'registration/attempt_failed.html', context={
            'error': kwargs['error'], 'title': 'Неудачная авторизация',
        })


class UserLogoutView(LogoutView):
    next_page = 'index'


class ProfileView(TemplateView, TitleMixin, AuthorizedOnlyDispatchMixin):
    model = MyUser
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')
    form_class = UserProfileForm
    title = 'Мой профиль'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = MyUser.objects.get(id=self.request.user.id)
        index = MyUser.objects.order_by('-score').filter(score__gte=user.score).count()
        context['index'] = index
        return context


class UserEdit(UpdateView, AuthorizedOnlyDispatchMixin):
    model = MyUser
    template_name = 'includes/profile_edit.html'
    success_url = reverse_lazy('users:profile')
    form_class = UserChangeProfileForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST, instance=request.user)
        if form.is_valid():
            form.save()
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            result = render_to_string('./includes/profile_data.html', request=request)
            return JsonResponse({'result': result})
        return redirect(self.success_url)

    def get(self, request, *args, **kwargs):
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            context = {'form': self.form_class(instance=request.user)}
            result = render_to_string('./includes/profile_edit.html', request=request, context=context)
            return JsonResponse({'result': result})


class UserImgEdit(UpdateView, AuthorizedOnlyDispatchMixin):
    model = MyUser
    template_name = 'includes/profile_img_edit.html'
    success_url = reverse_lazy('users:profile')

    def post(self, request, *args, **kwargs):
        user = MyUser.objects.get(id=request.user.id)
        img = request.FILES.get('image')
        if img:
            user.img = img
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


class UserPostCreateView(CreateView, AuthorizedOnlyDispatchMixin, TitleMixin):
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


class UserQuestionCreateView(CreateView, AuthorizedOnlyDispatchMixin, TitleMixin):
    """Creating a new question by a user"""
    model = Question
    template_name = 'user_activities/add_question.html'
    form_class = QuestionForm
    success_url = reverse_lazy('users:profile')
    title = 'Предложить свой вопрос'


class TopUsers(ListView, TitleMixin, AuthorizedOnlyDispatchMixin):
    """Shows users top-5"""
    model = MyUser
    template_name = 'user_activities/top_users.html'
    title = 'Топ-5 участников'
    context_object_name = 'top_users'

    def get_queryset(self):
        return MyUser.objects.filter(Q(is_active=True) & Q(score__gt=0)).order_by('-score')[:5]


class WriteToAdmin(FormView, TitleMixin, AuthorizedOnlyDispatchMixin):
    template_name = 'user_activities/write_to_admin.html'
    title = 'Написать письмо'
    form_class = WriteAdminForm

    def post(self, request, *args, **kwargs):
        username, email = request.user.username, request.user.email
        form = self.form_class(request.POST)
        if form.is_valid():
            try:
                subject = f"Пользователь {username} написал вам сообщение"
                context = {
                    'username': username,
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
            except Exception as e:
                logger.error(f'Ошибка отправки сообщения - {e}')
                form.add_error(None, 'Ошибка отправки сообщения')
        else:
            context = {
                'form': form,
                'username': username,
                'email': email,
            }
            return render(request, 'user_activities/write_to_admin.html', context)


class UserPasswordResetView(PasswordResetView, TitleMixin):
    form_class = MyPasswordResetForm
    title = 'Восстановление пароля'
    template_name = 'registration/password_reset.html'
    email_template_name = 'registration/pass_reset_email.html'
    subject_template_name = 'registration/pass_reset_subject.txt'
    from_email = EMAIL_HOST_USER

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            email = request.POST['email']
            context = {
                'email': email,
                'domain': DOMAIN_NAME,
            }
            form.save(DOMAIN_NAME, email_template_name=self.email_template_name,
                      subject_template_name=self.subject_template_name, from_email=self.from_email,
                      extra_email_context=context)
            return render(request, 'registration/password_reset_email_sent.html')
        else:
            return render(request, 'registration/password_reset.html', context={'form': form, })


class MyPasswordResetConfirmView(PasswordResetConfirmView, TitleMixin):
    template_name = 'registration/password_res_confirm.html'
    title = 'Создание нового пароля'


class MyPasswordResetCompleteView(PasswordResetCompleteView, TitleMixin):
    template_name = 'registration/password_res_complete.html'
    title = 'Пароль успешно изменен'


class GiveMeMyButtons(TemplateView):
    template_name = 'includes/profile_buttons.html'

    def get(self, request, *args, **kwargs):
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            result = render_to_string('includes/profile_buttons.html', request=request)
            return JsonResponse({'result': result})
