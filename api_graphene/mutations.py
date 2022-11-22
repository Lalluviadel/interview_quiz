"""Contains all mutations of the project."""
import graphene

from api_graphene.model_types import QuestionCategoryType, QuestionType, PostType, MyUserType
from posts.models import Post
from questions.models import Question, QuestionCategory
from users.models import MyUser


class CategoryInput(graphene.InputObjectType):
    """Input type for QuestionCategory Mutations."""
    id = graphene.ID()
    name = graphene.String()
    description = graphene.String()


class CreateCategory(graphene.Mutation):
    """QuestionCategory model create mutation."""
    class Arguments:
        input = CategoryInput(required=True)

    ok = graphene.Boolean()
    category = graphene.Field(QuestionCategoryType)

    @staticmethod
    def mutate(root, info, input=None):
        ok = True
        category_instance = QuestionCategory(name=input.name, description=input.description)
        category_instance.save()
        return CreateCategory(ok=ok, category=category_instance)


class ActiveBaseMutation(graphene.Mutation):
    """Parent mutation class for activation/deactivation objects."""
    model = None

    class Arguments:
        condition = graphene.Boolean()
        obj_id = graphene.ID()

    current_object = graphene.Field(QuestionCategoryType)

    @classmethod
    def mutate(cls, root, info, condition, obj_id):
        """Changes object condition (active/not active)."""
        mutating_object = cls.model.objects.get(pk=obj_id)
        mutating_object.available = condition
        mutating_object.save()
        return ActiveBaseMutation(current_object=mutating_object)


class ActiveCategory(ActiveBaseMutation):
    """QuestionCategory model activation/deactivation mutation."""
    model = QuestionCategory
    type = QuestionCategoryType
    current_object = graphene.Field(type)


class ActiveQuestion(ActiveBaseMutation):
    """Question model activation/deactivation mutation"""
    model = Question
    current_object = graphene.Field(QuestionType)


class ActivePost(ActiveBaseMutation):
    """Post model activation/deactivation mutation."""
    model = Post
    current_object = graphene.Field(PostType)


class ActiveMyUser(ActiveBaseMutation):
    """MyUser model activation/deactivation mutation."""
    model = MyUser
    current_object = graphene.Field(MyUserType)

    @classmethod
    def mutate(cls, root, info, condition, obj_id):
        """Changes MyUser condition (active/not active)"""
        user = cls.model.objects.get(pk=obj_id)
        user.is_active = condition
        user.save()
        return ActiveMyUser(current_object=user)
