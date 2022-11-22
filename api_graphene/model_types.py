"""Contains types for all project models for using in graphene scheme."""

from graphene_django import DjangoObjectType

from posts.models import Post
from questions.models import Question, QuestionCategory
from users.models import MyUser


class QuestionCategoryType(DjangoObjectType):
    """Type for QuestionCategory model description."""
    class Meta:
        model = QuestionCategory
        fields = '__all__'


class QuestionType(DjangoObjectType):
    """Type for Question model description."""
    class Meta:
        model = Question
        fields = '__all__'

class PostType(DjangoObjectType):
    """Type for Post model description."""
    class Meta:
        model = Post
        fields = '__all__'


class MyUserType(DjangoObjectType):
    """Type for MyUser model description."""
    class Meta:
        model = MyUser
        fields = '__all__'
