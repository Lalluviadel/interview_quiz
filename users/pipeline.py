from collections import OrderedDict
from datetime import datetime
from urllib.parse import urlunparse, urlencode

import requests
from django.utils import timezone
from social_core.exceptions import AuthForbidden

from users.models import MyUser


def save_new_user(backend, user, response, *args, **kwargs):
    """Authorization on site using VK-profile, if user younger than 10 y.o. authorization abort"""

    if backend.name != 'vk-oauth2':
        return

    api_url = urlunparse(('http', 'api.vk.com', '/method/users.get', None, urlencode(
        OrderedDict(fields=','.join(('bdate', 'first_name', 'last_name', 'photo')),
                    access_token=response['access_token'],
                    v=5.131)), None))

    resp = requests.get(api_url)
    if resp.status_code != 200:
        return

    data = resp.json()['response'][0]
    user.last_name = data['last_name']
    user.first_name = data['first_name']
    if data['photo']:
        photo_link = data['photo']
        photo_requests = requests.get(photo_link)

        user.username = user.first_name
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
        raise AuthForbidden('social_core.backends.vk.VK0Auth2')
    user.save()
