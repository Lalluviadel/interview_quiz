import graphene
from graphene_django.types import DjangoObjectType, ObjectType

from posts.models import Post
from questions.models import QuestionCategory, Question
from users.models import MyUser


class QuestionCategoryType(DjangoObjectType):
    class Meta:
        model = QuestionCategory
        fields = '__all__'


class QuestionType(DjangoObjectType):
    class Meta:
        model = Question
        fields = '__all__'


class Query(ObjectType):
    """Type for query"""
    all_categories = graphene.List(QuestionCategoryType)
    get_category_by_id = graphene.Field(QuestionCategoryType, cat_id=graphene.Int(required=True))
    all_questions = graphene.List(QuestionType)
    get_question_by_id = graphene.Field(QuestionType, cat_id=graphene.Int(required=True))


    def resolve_all_categories(root, info):
        return QuestionCategory.objects.all()

    def resolve_all_questions(root, info):
        return Question.objects.all()

    def resolve_get_category_by_id(root, info, cat_id):
        """Function for get project by its id"""
        try:
            return QuestionCategory.objects.get(id=cat_id)
        except QuestionCategory.DoesNotExist:
            return None

    def resolve_get_question_by_id(root, info, que_id):
        """Function for get project by its id"""
        try:
            return QuestionCategory.objects.get(id=que_id)
        except QuestionCategory.DoesNotExist:
            return None


class CategoryMutation(graphene.Mutation):
    """Todos model mutation"""

    class Arguments:
        condition = graphene.Boolean()
        cat_id = graphene.ID()

    category = graphene.Field(QuestionCategoryType)

    @classmethod
    def mutate(cls, root, info, condition, cat_id):
        """Changes todos condition (active/not active)"""
        category = QuestionCategory.objects.get(pk=cat_id)
        category.available = condition
        category.save()
        return CategoryMutation(category=category)


class QuestionMutation(graphene.Mutation):
    """Todos model mutation"""

    class Arguments:
        condition = graphene.Boolean()
        que_id = graphene.ID()

    question = graphene.Field(QuestionType)

    @classmethod
    def mutate(cls, root, info, condition, que_id):
        """Changes todos condition (active/not active)"""
        question = Question.objects.get(pk=que_id)
        question.available = condition
        question.save()
        return QuestionMutation(question=question)

class Mutation(graphene.ObjectType):
    update_category = CategoryMutation.Field()
    update_question = QuestionMutation.Field()

# Примеры запросов
#
# {
#   allCategories {
#     name
#     description
#     image
#     available
#   }
# }

# {
#   allQuestions {
#     subject {name}
#     question
#     rightAnswer
#     answer01
#     answer02
#     answer03
#     answer04
#     available
#     tag
#     image01
#     image02
#     image03
#     difficultyLevel
#     id
#   }
# }
# mutation updateQuestion {
#     updateQuestion(condition: false, queId: 1) {
#     question {
#         id
#         question
#         available
#         }
#     }
# }
