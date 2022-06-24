import logging
import sys
from django.test import TestCase

from users.models import MyUser
from ..models import Question, QuestionCategory

if len(sys.argv) > 1 and sys.argv[1] == 'test':
    logging.disable(logging.CRITICAL)

class TestQuestionCategoryModel(TestCase):
    """Test class for the QuestionCategory model"""

    @classmethod
    def setUpTestData(cls):
        """Set up non-modified QuestionCategory object used by all test methods"""
        QuestionCategory.objects.create(name='Python', description='a convenient programming language')

    def test_name_label(self):
        """QuestionCategory model name field Label test"""
        category = QuestionCategory.objects.get(id=1)
        field_label = category._meta.get_field('name').verbose_name
        self.assertEquals(field_label, 'name')

    def test_description_label(self):
        """QuestionCategory model description field Label test"""
        category = QuestionCategory.objects.get(id=1)
        field_label = category._meta.get_field('description').verbose_name
        self.assertEquals(field_label, 'description')

    def test_name_max_length(self):
        """QuestionCategory model name field max length test"""
        category = QuestionCategory.objects.get(id=1)
        max_length = category._meta.get_field('name').max_length
        self.assertEquals(max_length, 64)

    def test_string_output_of_the_model(self):
        """QuestionCategory model string output text test"""
        category = QuestionCategory.objects.get(id=1)
        expected_string_output = category.name
        self.assertEquals(expected_string_output, str(category))

    def test_default_available_true(self):
        """QuestionCategory model available field default is True test"""
        category = QuestionCategory.objects.get(id=1)
        self.assertEquals(category.available, True)


class TestQuestionModel(TestCase):
    """Test class for the Question model"""

    @classmethod
    def setUpTestData(cls):
        """Set up non-modified Question, MyUser and QuestionCategory objects used by all test methods"""
        QuestionCategory.objects.create(name='Python', description='a convenient programming language')
        MyUser.objects.create(first_name='Quentin', last_name='Tarantino', email='queenteen@mail.ru')
        MyUser.objects.create(username='drf', email='example@mail.ru')
        Question.objects.create(question='Что делает функция strip()?',
                                right_answer='Возвращает копию исходной строки с удалением начальных '
                                             'и конечных пробелов и/или указанных символов',
                                answer_01='Возвращает копию исходной строки с удалением начальных '
                                          'и конечных пробелов и/или указанных символов',
                                answer_02='Возвращает оригинал исходной строки с удалением начальных '
                                          'и конечных пробелов и/или указанных символов',
                                answer_03='Возвращает копию исходного списка с удалением первого '
                                          'и последнего элементов и/или элементов с указанными порядковыми номерами',
                                answer_04='Возвращает оригинал исходного списка с удалением первого '
                                          'и последнего элементов и/или элементов с указанными порядковыми номерами')
        Question.objects.create(question='Текст вопроса')

    def test_question_max_length(self):
        """Question model name field max length test"""
        question = Question.objects.first()
        max_length = question._meta.get_field('question').max_length
        self.assertEquals(max_length, 250)

    def test_question_subject_default(self):
        """Question model subject(category) field default is QuestionCategory object with id=1"""
        question = Question.objects.first()
        category = QuestionCategory.objects.first()
        self.assertEquals(question.subject, category)

    def test_question_author_default(self):
        """Question model author field default is MyUser object with nickname=drf"""
        question = Question.objects.first()
        author = MyUser.objects.get(username='drf')
        self.assertEquals(question.author, author)

    def test_right_answer_default(self):
        """Question model right answer field default test"""
        question = Question.objects.get(id=2)
        self.assertEquals(question.right_answer, 'default')

    def test_right_answer_max_length(self):
        """Question model right answer field max length test"""
        question = Question.objects.get(id=2)
        max_length = question._meta.get_field('right_answer').max_length
        self.assertEquals(max_length, 150)

    def test_answers_default(self):
        """Question model answers fields default test"""
        question = Question.objects.get(id=2)
        for item in (question.answer_01, question.answer_02,
                     question.answer_03, question.answer_04):
            self.assertEquals(item, 'default')

    def test_answers_max_length(self):
        """Question model answers fields max length test"""
        question = Question.objects.get(id=2)
        for item in ('answer_01', 'answer_02',
                     'answer_03', 'answer_04'):
            max_length = question._meta.get_field(item).max_length
        self.assertEquals(max_length, 150)

    def test_difficulty_level_label(self):
        """Question model difficulty level field Label test"""
        question = Question.objects.first()
        field_label = question._meta.get_field('difficulty_level').verbose_name
        self.assertEquals(field_label, 'уровень')

    def test_difficulty_level_default(self):
        """Question model difficulty level field default test"""
        question = Question.objects.first()
        self.assertEquals(question.difficulty_level, 'NB')

    def test_difficulty_level_max_length(self):
        """Question model difficulty level field max length test"""
        question = Question.objects.first()
        max_length = question._meta.get_field('difficulty_level').max_length
        self.assertEquals(max_length, 2)

    def test_available_default(self):
        """Question model available field default test"""
        question = Question.objects.first()
        self.assertFalse(question.available)

    def test_tag_default(self):
        """Question model difficulty level field default test"""
        question = Question.objects.first()
        self.assertEquals(question.tag, 'IT')

    def test_tag_max_length(self):
        """Question model difficulty level field max length test"""
        question = Question.objects.first()
        max_length = question._meta.get_field('tag').max_length
        self.assertEquals(max_length, 250)

    def test_string_output_of_the_model(self):
        """"Question model string output text test"""
        question = Question.objects.first()
        expected_string_output = question.question
        self.assertEquals(expected_string_output, str(question))
