from django.urls import path

from questions.views import CategoryView, categories, QuestionView, \
    answers

app_name = 'questions'
urlpatterns = [
    path('categories/', categories, name='categories'),
    path('start_test/<int:pk>/', CategoryView.as_view(), name='start_test'),
    path('test_body/<int:pk>/', QuestionView.as_view(), name='test_body'),
    path('answers/<int:item_id>/', answers, name='answers'),
]
