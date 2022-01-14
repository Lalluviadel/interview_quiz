from django.contrib import admin
from .models import Question, QuestionCategory

admin.site.register(Question)
admin.site.register(QuestionCategory)
