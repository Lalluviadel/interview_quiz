from django.conf import settings
from django.conf.urls import handler404
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import routers

from api.api import QuestionCategoryViewSet, QuestionViewSet, PostViewSet, UserViewSet
from questions.views import MainView, my_handler404

router = routers.DefaultRouter()
router.register('categories', QuestionCategoryViewSet)
router.register('questions', QuestionViewSet)
router.register('posts', PostViewSet)
router.register('users', UserViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', MainView.as_view(), name='index'),
    path('questions/', include('questions.urls', namespace='questions')),
    path('users/', include('users.urls', namespace='users')),
    path('myadmin/', include('myadmin.urls', namespace='myadmin')),
    path('posts/', include('posts.urls', namespace='posts')),

    path('', include('social_django.urls', namespace='social')),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/', include(router.urls)),
]

handler404 = 'questions.views.my_handler404'

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [re_path(r'^__debug_/', include(debug_toolbar.urls))]
    urlpatterns += [path('404/', my_handler404, kwargs={'exception':
                                                            Exception('Page not Found')}, name='page_404')]
