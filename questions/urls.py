from django.urls import path

from questions.views import CategoryView, QuestionView, AllCategoriesView, \
    TimeIsUp, AnswerQuestion

app_name = 'questions'
urlpatterns = [
    path('categories/', AllCategoriesView.as_view(), name='categories'),
    path('start_test/<int:pk>/', CategoryView.as_view(), name='start_test'),
    path('test_body/<int:pk>/', QuestionView.as_view(), name='test_body'),
    path('answers/<int:item_id>/', AnswerQuestion.as_view(), name='answers'),
    path('time_is_up/', TimeIsUp.as_view(), name='time_is_up'),
]
