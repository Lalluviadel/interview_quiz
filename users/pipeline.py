"""Allows you to register and authorize using the VK social network profile.
Retrieves all the necessary data for registration and the user's avatar from the profile.
Activation of the profile on the site with this option of registration is not required."""
from collections import OrderedDict
from datetime import datetime
from urllib.parse import urlunparse, urlencode

import requests
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from social_core.exceptions import AuthForbidden

from users.models import MyUser

import logging

logger = logging.getLogger(__name__)

USER_FIELDS = ['username', 'email']


def save_new_user(backend, user, response, *args, **kwargs):
    """Authorization on site using the VK social network profile,
    Performs parsing of profile data. If the user is already registered,
    returns. If not, a check is performed to see if the profile email
    has been used for another registration before. Then the age of the user
    is calculated according to the data that he indicated in his profile
    in the VK social network. If the user is under 10 years old, registration
    is interrupted, access is denied.

    Note:
        This registration method is only suitable for those profiles
        in which the email is specified. If a phone number was used to
        register a profile in the VK, this profile cannot be used for
        registration on the site.
    """

    if backend.name != 'vk-oauth2':
        return

    api_url = urlunparse(('http', 'api.vk.com', '/method/users.get', None, urlencode(
        OrderedDict(fields=','.join(('bdate', 'first_name', 'last_name', 'photo_max')),
                    access_token=response['access_token'],
                    v=5.131)), None))

    resp = requests.get(api_url)
    if resp.status_code != 200:
        return

    data = resp.json()['response'][0]
    user.last_name = data['last_name']
    user.first_name = data['first_name']
    if data['photo_max']:
        photo_link = data['photo_max']
        photo_requests = requests.get(photo_link)

        path_photo = f'user_images/vk_{user.first_name}_{user.last_name}.jpg'
        with open(f'media/{path_photo}', 'wb') as photo:
            photo.write(photo_requests.content)
        user.img = path_photo

    bdate = datetime.strptime(data['bdate'], '%d.%m.%Y').date()

    if response['email'] and not MyUser.objects.filter(email=response['email']).exists():
        user.email = response['email']

    age = timezone.now().date().year - bdate.year
    if age < 10:
        user.delete()
        logger.warning('VK - Попытка регистрации ребенка младше 10 лет')
        raise AuthForbidden('social_core.backends.vk.VK0Auth2')
    user.is_active = True
    user.save()


def if_user_exists_pipeline(request, details, backend, **kwargs):
    """
    Checks the data for user authorization through the profile in the VK
    social network. If all the data correspond to the data associated with
    the email address used, the user is logged in.

    If there is no email address in this VK profile or this address has already been used for registration,
    a message about this is generated for the user and authorization is rejected.
    """
    fields = {name: kwargs.get(name, details.get(name))
              for name in backend.setting('USER_FIELDS', USER_FIELDS)}
    if fields['email']:
        try:
            user = MyUser.objects.get(email=fields['email'])
            if user.first_name == details['first_name'] and user.last_name == details['last_name'] and \
                    user.username == details['username']:
                auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return HttpResponseRedirect(reverse('index'))
            else:
                logger.warning(f'VK - Попытка повторной регистрации на тот же email {fields["email"]}')
                msg = 'Пользователь с таким email уже зарегистрирован'
                return HttpResponseRedirect(reverse('users:failed', kwargs={'error': msg}))
        except Exception as e:
            logger.error(f'VK - Ошибка проверки пользователя - {e}')
    else:
        logger.warning(f'VK - Попытка авторизации с аккаунтом без email')
        msg = 'Ваш профиль VK создан с использованием номера телефона, а не email в ' \
              'качестве логина. К сожалению, политика VK не предоставляет в данном случае ' \
              'email пользователя, поэтому вы не сможете залогиниться на сайте, используя ' \
              'профиль VK'
        return HttpResponseRedirect(reverse('users:failed', kwargs={'error': msg}))
