from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path

from questions.views import MainView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', MainView.as_view(), name='index'),
    path('questions/', include('questions.urls', namespace='questions')),
    path('users/', include('users.urls', namespace='users')),
    path('myadmin/', include('myadmin.urls', namespace='myadmin')),
    path('posts/', include('posts.urls', namespace='posts')),

    path('', include('social_django.urls', namespace='social')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    import debug_toolbar

    urlpatterns += [re_path(r'^__debug_/', include(debug_toolbar.urls))]
