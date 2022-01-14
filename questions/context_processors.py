from questions.models import QuestionCategory, Question
from users.models import MyUser


def categories(request):
    return {
        'categories': QuestionCategory.objects.all(),
    }

def users(request):
    return {
        'users': MyUser.objects.all(),
    }

def questions(request):
    return {
        'questions': Question.objects.all(),
    }
