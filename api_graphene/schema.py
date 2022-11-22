"""Graphene API schema."""

import graphene
from graphene_django.types import ObjectType

from api_graphene.model_types import QuestionCategoryType, QuestionType, PostType, MyUserType
from api_graphene.mutations import CreateCategory, \
    ActiveQuestion, ActivePost, ActiveMyUser, ActiveCategory
from posts.models import Post
from questions.models import QuestionCategory, Question
from users.models import MyUser


class Query(ObjectType):
    """Type for query."""
    all_categories = graphene.List(QuestionCategoryType)
    get_category_by_id = graphene.Field(QuestionCategoryType, cat_id=graphene.Int(required=True))

    all_questions = graphene.List(QuestionType)
    get_question_by_id = graphene.Field(QuestionType, que_id=graphene.Int(required=True))
    get_questions_by_category = graphene.List(QuestionType, name=graphene.String(required=False))

    all_posts = graphene.List(PostType)
    get_post_by_id = graphene.Field(PostType, post_id=graphene.Int(required=True))

    all_users = graphene.List(MyUserType)
    get_user_by_id = graphene.Field(MyUserType, user_uuid=graphene.UUID(required=True))

    def resolve_all_categories(self, info):
        """Returns all categories."""
        return QuestionCategory.objects.all()

    def resolve_get_category_by_id(self, info, cat_id):
        """Returns the category by its id or None if not exists."""
        try:
            return QuestionCategory.objects.get(id=cat_id)
        except QuestionCategory.DoesNotExist:
            return None

    def resolve_all_questions(self, info):
        """Returns all questions."""
        return Question.objects.all()

    def resolve_get_question_by_id(self, info, que_id):
        """Returns the question by its id or None if not exists."""
        try:
            return Question.objects.get(id=que_id)
        except Question.DoesNotExist:
            return None

    def resolve_get_questions_by_category(self, info, name=None):
        """Returns questions by its category name or all questions if
        category with current name not exists."""
        if name:
            return Question.objects.filter(subject__name=name)
        return Question.objects.all()

    def resolve_all_posts(self, info):
        """Returns all posts."""
        return Post.objects.all()

    def resolve_get_post_by_id(self, info, post_id):
        """Returns the post by its id or None if not exists."""
        try:
            return Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return None

    def resolve_all_users(self, info):
        """Returns all users."""
        return MyUser.objects.all()

    def resolve_get_user_by_id(self, info, user_uuid):
        """Returns the user by its id or None if not exists."""
        try:
            return MyUser.objects.get(id=user_uuid)
        except MyUser.DoesNotExist:
            return None


class Mutation(graphene.ObjectType):
    """A common class for all mutations of the project."""
    create_category = CreateCategory.Field()
    activate_category = ActiveCategory.Field()
    activate_question = ActiveQuestion.Field()
    activate_post = ActivePost.Field()
    activate_user = ActiveMyUser.Field()
