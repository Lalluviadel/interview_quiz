"""
Views for user interaction with.

The submodule contains views for a full-fledged user interaction
with the content of the site.

Here are the views:

    * to register a new user and verify a registration of a profile;
    * to log in and log out of the profile;
    * to view and edit the user's profile;
    * to create a user's own post, question, or a message for the admin;
    * to recover forgotten password;
    * to view the Top-5 participants of the site;
    * to refuse to view information about the testing procedure;
    * for profile menu buttons;

"""
import logging
from smtplib import SMTPAuthenticationError

from django.contrib import auth, messages
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordResetCompleteView,
    PasswordResetConfirmView, PasswordResetView
)
from django.core.mail import send_mail
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import HttpResponseRedirect, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView, FormView, ListView,
    TemplateView, UpdateView
)

from interview_quiz.mixin import (
    AuthorizedOnlyDispatchMixin, TitleMixin
)
from interview_quiz.settings import DOMAIN_NAME, EMAIL_HOST_USER

from myadmin.forms import PostForm, QuestionForm

from posts.models import Post

from questions.models import Question

from user_log.helpers import (
    auth_update_user_logging, create_user_logging
)

from users.forms import (
    MyPasswordResetForm, UserChangeProfileForm,
    UserImgChangeProfileForm, UserLoginForm,
    UserProfileForm, UserRegisterForm, WriteAdminForm
)
from users.models import MyUser

logger = logging.getLogger(__name__)


class UserLoginView(LoginView, TitleMixin):
    """A view for authorization."""

    template_name = 'registration/login.html'
    title = 'Авторизация'
    form_class = UserLoginForm

    def post(self, request, *args, **kwargs):
        """
        Perform user authorization.

        Authorization is performed only for active users
        (who have verified their profile with a link received by email).
        """
        form = self.form_class(data=request.POST)
        if form.is_valid():
            user = auth.authenticate(
                username=request.POST['username'],
                password=request.POST['password']
            )
            if user.is_active:
                auth.login(request, user)
                auth_update_user_logging(user)
                return HttpResponseRedirect(reverse('index'))
        else:
            return render(
                request, 'registration/login.html',
                context={'form': form, }
            )


class RegisterView(FormView, TitleMixin):
    """A view for registering a new user."""

    template_name = 'registration/register.html'
    title = 'Регистрация нового пользователя'
    form_class = UserRegisterForm

    def post(self, request, *args, **kwargs):
        """
        Perform registration of a new user.

        Both in case of success and in case of failure, a message is generated
        that shows the user the result of registration.
        Starts the verification process of the new profile.
        """
        form = self.form_class(data=request.POST)
        if form.is_valid():
            user = form.save()
            try:
                if self.send_verify_link(user):
                    messages.success(
                        request,
                        'Для завершения регистрации используйте ссылку '
                        'из письма, отправленного на email, указанный '
                        'при регистрации.'
                    )
                    create_user_logging(user)

                else:
                    msg = (
                        'К сожалению, произошел сбой, письмо для завершения '
                        'регистрации не было отослано. Для активации вашего '
                        f'профиля напишите письмо на адрес {EMAIL_HOST_USER}'
                    )
                    messages.error(request, msg)
                return HttpResponseRedirect(reverse('users:register'))
            except SMTPAuthenticationError:
                messages.error(
                    request,
                    ('К сожалению, произошел сбой. Пользователь с '
                     'указанными данными не был зарегистрирован.')
                )
                logger.error('SMTPAuthenticationError while user registration')
                user.delete()
                return render(
                    request, 'registration/register.html',
                    context={'form': form, }
                )
        else:
            messages.error(
                request,
                'Убедитесь, что вы ввели корректные данные.'
            )
            logger.warning('Неудачная попытка регистрации пользователя')
        return render(
            request, 'registration/register.html',
            context={'form': form, }
        )

    @staticmethod
    def send_verify_link(user):
        """
        Send to user an email with verification link.

        Args:
            * user(MyUser):
            the user object that was created during registration;
        """
        verify_link = reverse(
            'users:verify',
            args=[user.email, user.activation_key]
        )
        subject = f'Подтверждение регистрации на сайте {DOMAIN_NAME}'
        context = {
            'my_user': user.username,
            'my_site_name': DOMAIN_NAME,
            'my_link': f'{DOMAIN_NAME}{verify_link}',
        }
        message = render_to_string('registration/activation_msg.html', context)
        return send_mail(subject, message, EMAIL_HOST_USER, [user.email],
                         html_message=message, fail_silently=False)


class Verify(TemplateView, TitleMixin):
    """A view for activating and authorizing a new user."""

    title = 'Успешная активация профиля'

    def get(self, request, *args, **kwargs):
        """
        Check an activation key.

        Checks the validity period of the activation key and its
        compliance with the one that is in the activation link sent
        to the user. If successful, the user becomes active and logs in.
        In case of failure, an appropriate message is generated to
        inform the user about this and further options for action.
        """
        try:
            user = MyUser.objects.get(email=kwargs['email'])

            if user.is_activation_key_expired():
                msg = (
                    'Ваш ключ активации устарел. Для активации '
                    'вашего профиля напишите письмо на адрес '
                    f'{EMAIL_HOST_USER} или зарегистрируйте новый '
                    'профиль, используя другой email.'
                )
                logger.error(
                    'Сбой активации нового пользователя - '
                    'устаревший ключ активации'
                )
                return HttpResponseRedirect(reverse(
                    'users:failed', kwargs={'error': msg}
                ))

            elif user and user.activation_key == kwargs['activation_key']:
                user.activation_key, user.activation_key_created = '', None
                user.is_active = True
                auth.login(
                    request, user,
                    backend='django.contrib.auth.backends.ModelBackend'
                )
                user.save()
                auth_update_user_logging(user)
                return render(request, 'registration/verification.html')

            else:
                raise ValueError(
                    'Несовпадение ключа активации из письма '
                    'с присвоенным пользователю'
                )

        except Exception as e:
            logger.error('Сбой активации нового пользователя %s', e)
            msg = (
                f'Сбой активации. Попробуйте использовать ссылку,'
                'полученную в письме, повторно. '
                f'В случае неудачи напишите на адрес {EMAIL_HOST_USER},'
                f'указав причину обращения.'
            )
            return HttpResponseRedirect(reverse(
                'users:failed', kwargs={'error': msg})
            )


class FailedAuthenticationView(TemplateView):
    """
    View for failed authorization completion.

    If activation user's profile or VK-authentication is failed,
    the user will be redirected with an error message.
    """

    def get(self, request, *args, **kwargs):
        """
        Get auth failed message.

        Receives an error message that was made during
        authorization and passes it to the context.
        """
        return render(request, 'registration/attempt_failed.html', context={
            'error': kwargs['error'], 'title': 'Неудачная авторизация',
        })


class UserLogoutView(LogoutView):
    """A view for the user to log out of the profile."""

    next_page = 'index'


class ProfileView(TemplateView, TitleMixin, AuthorizedOnlyDispatchMixin):
    """A view for the user to view their profile."""

    model = MyUser
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')
    form_class = UserProfileForm
    title = 'Мой профиль'

    def get_context_data(self, **kwargs):
        """
        Get user's rating position.

        Gets data about where the user is in the rating and
        transmits it to the context. The template displays the
        rating only when the user's score is greater than 0.
        """
        context = super().get_context_data(**kwargs)
        user = MyUser.objects.get(id=self.request.user.id)
        index = MyUser.objects.order_by('-score').filter(
            score__gte=user.score).count()
        context['index'] = index
        return context


class UserEdit(UpdateView, AuthorizedOnlyDispatchMixin):
    """A view for the user to edit their profile."""

    model = MyUser
    template_name = 'includes/profile_edit.html'
    success_url = reverse_lazy('users:profile')
    form_class = UserChangeProfileForm

    def post(self, request, *args, **kwargs):
        """
        Edit user's profile.

        Retrieves data from the profile editing form and,
        if valid, saves new user profile data.
        When using AJAX, it allows you to update data without
        completely reloading the page.
        """
        form = self.form_class(data=request.POST, instance=request.user)
        if form.is_valid():
            form.save()
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            result = render_to_string(
                './includes/profile_data.html',
                request=request
            )
            return JsonResponse({'result': result})
        return redirect(self.success_url)

    def get(self, request, *args, **kwargs):
        """Retrieve data from the profile editing form using AJAX."""
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            context = {'form': self.form_class(instance=request.user)}
            result = render_to_string(
                './includes/profile_edit.html', request=request,
                context=context
            )
            return JsonResponse({'result': result})


class UserImgEdit(UpdateView, AuthorizedOnlyDispatchMixin):
    """A view for the user to edit their avatar."""

    model = MyUser
    template_name = 'includes/profile_img_edit.html'
    success_url = reverse_lazy('users:profile')

    def post(self, request, *args, **kwargs):
        """
        Save the new avatar selected by the user.

        When using AJAX, data is updated without reloading the entire page.
        """
        user = MyUser.objects.get(id=request.user.id)
        img = request.FILES.get('image')
        if img:
            user.img = img
            user.save(update_fields=['img'])
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            context = {'user': user}
            result = render_to_string(
                './includes/profile_img.html', request=request,
                context=context
            )
            return JsonResponse({'result': result})
        return redirect(self.success_url)

    def get(self, request, *args, **kwargs):
        """Retrieve data from the image editing form using AJAX."""
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            context = {'form': UserImgChangeProfileForm(instance=request.user)}
            result = render_to_string(
                './includes/profile_img_edit.html', request=request,
                context=context
            )
            return JsonResponse({'result': result})


class UserPostCreateView(CreateView, AuthorizedOnlyDispatchMixin, TitleMixin):
    """A view for creating a new post by a user."""

    model = Post
    template_name = 'user_activities/add_post.html'
    form_class = PostForm
    success_url = reverse_lazy('users:profile')
    title = 'Написать свою статью'

    def post(self, request, *args, **kwargs):
        """
        Create a new post by the user.

        Receives data from the user's post creation form,
        with their validity, the post is saved, but is inactive.
        If the creation of the post is successful, an email is sent
        notifying the admin about it, and the user sees a modal window
        with information about success. In case of failure, the user
        sees a form with the data filled in by him and an indication
        of the error. AJAX is involved in both cases.
        """
        data = request.POST.copy()
        form = self.form_class(data=data)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            if request.FILES.get('image'):
                post.image = request.FILES.get('image')
            post.save()
            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                return JsonResponse({'is_valid': True})
            return redirect(self.success_url)
        else:
            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                result = render_to_string(
                    'includes/post_form.html',
                    request=request, context={'form': form, }
                )
                return JsonResponse({'result': result})
            return render(
                request, 'user_activities/add_post.html',
                context={'form': form, }
            )


class UserQuestionCreateView(
    CreateView, AuthorizedOnlyDispatchMixin,
    TitleMixin
):
    """A view for creating a new question by a user."""

    model = Question
    template_name = 'user_activities/add_question.html'
    form_class = QuestionForm
    success_url = reverse_lazy('users:profile')
    title = 'Предложить свой вопрос'

    def post(self, request, *args, **kwargs):
        """
        Create a new question by the user.

        Receives data from the user's question creation form,
        with their validity, the question is saved, but is inactive.
        If the creation of the question is successful, an email is
        sent notifying the admin about it, and the user sees a modal
        window with information about success. In case of failure,
        the user sees a form with the data filled in by him and an
        indication of the error. AJAX is involved in both cases.
        """
        data = request.POST.copy()
        form = self.form_class(data=data)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            for image in ('image_01', 'image_02', 'image_03'):
                setattr(question, image, request.FILES.get(image))
            question.save()
            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                return JsonResponse({'is_valid': True})
            return redirect(self.success_url)
        else:
            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                result = render_to_string(
                    'includes/question_form.html', request=request,
                    context={'form': form, }
                )
                return JsonResponse({'result': result})
            return render(
                request, 'user_activities/add_question.html',
                context={'form': form, }
            )


class TopUsers(ListView, TitleMixin, AuthorizedOnlyDispatchMixin):
    """View to display users Top-5."""

    model = MyUser
    template_name = 'user_activities/top_users.html'
    title = 'Топ-5 участников'
    context_object_name = 'top_users'

    def get_queryset(self):
        """
        Get Top-5 users.

        Returns a sorted queryset of 5 participants
        with the highest total score.
        """
        return MyUser.objects.filter(
            Q(is_active=True) & Q(score__gt=0)).order_by('-score')[:5]


class WriteToAdmin(FormView, TitleMixin, AuthorizedOnlyDispatchMixin):
    """View for writing a message to the admin on his email."""

    template_name = 'user_activities/write_to_admin.html'
    title = 'Написать письмо'
    form_class = WriteAdminForm

    def post(self, request, *args, **kwargs):
        """
        Send email to the admin.

        Generates an email for the admin and starts form validation.
        If successful, the message is sent and the user is redirected
        to his profile page.
        In case of failure, the user sees a form with the data entered
        by him and an indication of the error.
        Additionally, a pop-up modular window informs him about the
        progress of sending a message.
        """
        username, email = request.user.username, request.user.email
        form = self.form_class(request.POST)
        if form.is_valid():
            try:
                subject = f'Пользователь {username} написал вам сообщение'
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
                if request.META.get(
                        'HTTP_X_REQUESTED_WITH'
                ) == 'XMLHttpRequest':
                    return JsonResponse({'is_valid': True})

                return redirect(reverse_lazy('users:profile'))
            except Exception as e:
                logger.error('Ошибка отправки сообщения - %s', e)
                form.add_error(None, 'Ошибка отправки сообщения')
        else:
            context = {
                'form': form,
                'username': username,
                'email': email,
            }
            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                result = render_to_string(
                    'includes/letter_form.html',
                    request=request, context=context
                )
                return JsonResponse({'result': result})
            return render(
                request, 'user_activities/write_to_admin.html',
                context=context
            )


class UserPasswordResetView(PasswordResetView, TitleMixin):
    """A view to request password recovery."""

    form_class = MyPasswordResetForm
    title = 'Восстановление пароля'
    template_name = 'registration/password_reset.html'
    email_template_name = 'registration/pass_reset_email.html'
    subject_template_name = 'registration/pass_reset_subject.txt'
    from_email = EMAIL_HOST_USER

    def post(self, request, *args, **kwargs):
        """
        Send password restore email.

        Generates and sends the user an email with a link
        to restore the password.
        """
        form = self.form_class(data=request.POST)
        if form.is_valid():
            email = request.POST['email']
            context = {
                'email': email,
                'domain': DOMAIN_NAME,
            }
            form.save(
                DOMAIN_NAME, email_template_name=self.email_template_name,
                subject_template_name=self.subject_template_name,
                from_email=self.from_email,
                extra_email_context=context
            )
            return render(
                request, 'registration/password_reset_email_sent.html',
                {'title': self.title}
            )
        return render(
            request, 'registration/password_reset.html',
            context={'form': form, 'title': self.title}
        )


class MyPasswordResetConfirmView(PasswordResetConfirmView, TitleMixin):
    """
    Create a new password.

    A view for creating and saving a new password in case
    the previous password was lost by the user.
    """

    template_name = 'registration/password_res_confirm.html'
    title = 'Создание нового пароля'


class MyPasswordResetCompleteView(PasswordResetCompleteView, TitleMixin):
    """
    Password reset complete view.

    A view to inform the user about the successful change
    (recovery) of the password.
    """

    template_name = 'registration/password_res_complete.html'
    title = 'Пароль успешно изменен'


class GiveMeMyButtons(TemplateView):
    """
    Display user menu buttons.

    A view for displaying user menu buttons when visiting
    your profile. AJAX is used.
    """

    template_name = 'includes/profile_buttons.html'

    def get(self, request, *args, **kwargs):
        """
        Return user buttons.

        Returns json with the prepared html code of
        the user menu buttons.
        """
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            result = render_to_string(
                'includes/profile_buttons.html', request=request
            )
            return JsonResponse({'result': result})


class UserNoInfo(TemplateView):
    """
    Refuse further viewing of an info pop-up modal window.

    A view to refuse further viewing of a pop-up modal
    window with information about the order of testing
    at its start. If the user no longer wants to see it,
    he can tick the checkbox of this modular window.
    A change will be made to the entry in the database
    corresponding to his profile, and the window with information
    for him will no longer appear.
    """

    template_name = 'includes/no_info_success.html'

    def post(self, request, *args, **kwargs):
        """
        Stop the appearance of an information window.

        Receives data on the need to stop the appearance of an
        information window for this user and makes appropriate changes.
        """
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' \
                and request.POST['flag'] == 'true':
            user = MyUser.objects.get(id=request.user.id)
            user.info = False
            user.save()
            result = render_to_string(self.template_name, request=request)
            return JsonResponse({'result': result})
