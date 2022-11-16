"""
Contains classes that provide sets of API views for all models of the project.
"""
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from posts.models import Post
from questions.models import QuestionCategory, Question
from users.models import MyUser
from .filters import QuestionFilter, QuestionCategoryFilter, PostFilter, UserFilter
from .serializers import QuestionCategorySerializer, QuestionSerializer, \
    PostSerializer, UserSerializer


class BasePagination(LimitOffsetPagination):
    """A class for pagination of the result."""
    default_limit = 10


class BaseViewSet(ModelViewSet):
    """Basic class of making set of api views."""
    model = QuestionCategory
    pagination_class = BasePagination
    filter_backends = (DjangoFilterBackend,)
    permission_classes = [AllowAny]
    permission_classes_by_action = {
        'create': [IsAuthenticated],
        'update': [IsAdminUser],
        'partial_update': [IsAdminUser],
        'destroy': [IsAdminUser]
    }

    def get_permissions(self):
        """Returns a list of permission classes for each HTTP method.
        If they are not defined, returns the common permission class level for all methods.
        """
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes]

    def destroy(self, request, *args, **kwargs):
        """When trying to delete an object, makes it inactive
        (or active if it was deactivated earlier).
        """
        item = get_object_or_404(self.queryset, pk=kwargs['pk'])
        item.available = not item.available
        item.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        """Overrides the method of creating a new object.
        If it is not an instance of a Category, it automatically fills in the 'author' field
        with the data of the current user."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user) \
            if self.model is not QuestionCategory else serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, name='Сортировка по тегу (а-я)')
    def order_by_tag(self, request, *args, **kwargs):
        """A method that allows you to sort the queryset by the 'tag' field."""
        items = self.model.objects.all().order_by('tag')
        page = self.paginate_queryset(items)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)


class QuestionCategoryViewSet(BaseViewSet):
    """Child class for QuestionCategory model api views."""
    queryset = QuestionCategory.objects.all().order_by('name')
    http_method_names = ['get', 'post', 'put']
    serializer_class = QuestionCategorySerializer
    filterset_class = QuestionCategoryFilter
    permission_classes_by_action = {item: [IsAdminUser] for item in
                                    ['create', 'update', 'partial_update', ]}

    @action(detail=False, name='Сортировка по количеству вопросов')
    def order_by_tag(self, request, *args, **kwargs):
        """Overrides parent's method for ordering question categories by question quantity."""
        items = QuestionCategory.objects.all().annotate(que_set=Count('question')) \
            .order_by('-que_set')
        page = self.paginate_queryset(items)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)


class QuestionViewSet(BaseViewSet):
    """Child class for Question model api views."""
    model = Question
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    filterset_class = QuestionFilter


class PostViewSet(BaseViewSet):
    """Child class for Post model api views."""
    model = Post
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filterset_class = PostFilter


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """Class for MyUser model api views."""
    queryset = MyUser.objects.all()
    serializer_class = UserSerializer
    pagination_class = BasePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = UserFilter
    permission_classes = [IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        """When trying to delete an object, makes it inactive
        (or active if it was deactivated earlier).
        """
        item = get_object_or_404(self.queryset, pk=kwargs['pk'])
        item.is_active = not item.is_active
        item.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, name='Пользователи по дате последнего логина')
    def recent_users(self, request, *args, **kwargs):
        """A method that allows you to sort users by the 'last_login' field."""
        recent_users = MyUser.objects.all().order_by('-last_login')

        page = self.paginate_queryset(recent_users)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(recent_users, many=True)
        return Response(serializer.data)

    @action(detail=False, name='Пользователи по рейтингу')
    def ranking_by_score(self, request, *args, **kwargs):
        """A method that allows you to sort users by the 'score' field."""
        users_by_score = MyUser.objects.all().order_by('-score')

        page = self.paginate_queryset(users_by_score)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(users_by_score, many=True)
        return Response(serializer.data)
