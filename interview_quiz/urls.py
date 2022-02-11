from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from questions.views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('questions/', include('questions.urls', namespace='questions')),
    path('users/', include('users.urls', namespace='users')),
    path('myadmin/', include('myadmin.urls', namespace='myadmin')),
    path('posts/', include('posts.urls',namespace='posts')),

    path('', include('social_django.urls',namespace='social')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
