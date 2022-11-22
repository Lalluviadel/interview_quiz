"""Contains filters for project API."""
from django_filters.rest_framework import BooleanFilter, \
    DateFromToRangeFilter, FilterSet, ChoiceFilter, ModelChoiceFilter, \
    RangeFilter, CharFilter
from django_filters.widgets import RangeWidget

from posts.models import Post
from questions.models import Question, QuestionCategory
from users.models import MyUser


DIFFICULTY_LEVEL_CHOICES = (
        ('NB', 'новичок'),
        ('AV', 'середнячок'),
        ('SP', 'умник'),
    )


class QuestionFilter(FilterSet):
    """
    Filter for objects of the Question model by different criteria.
    """
    question = CharFilter(lookup_expr='contains', label='Текст вопроса содержит:')
    subject__name = ModelChoiceFilter(queryset=QuestionCategory.objects.all(), label='Название категории:')
    author__name = CharFilter(lookup_expr='contains', label='Никнейм автора содержит:')
    available = BooleanFilter(field_name='available', label='Опубликован:')
    difficulty_level = ChoiceFilter(choices=DIFFICULTY_LEVEL_CHOICES, label='Уровень сложности:')
    tag = CharFilter(lookup_expr='contains', label='Тэг содержит:')

    class Meta:
        model = Question
        fields = ['question', 'subject__name', 'author__name', 'difficulty_level', 'available', 'tag', ]


class QuestionCategoryFilter(FilterSet):
    """
    Filter for objects of the QuestionCategory model by different criteria.
    """
    name = CharFilter(lookup_expr='contains', label='Название категории содержит:')
    available = BooleanFilter(field_name='available', label='Активна:')

    class Meta:
        model = QuestionCategory
        fields = ['name', 'available', ]


class PostFilter(FilterSet):
    """
    Filter for objects of the Post model by different criteria.
    """
    title = CharFilter(lookup_expr='contains', label='Название содержит:')
    category__name = ModelChoiceFilter\
        (queryset=QuestionCategory.objects.all(), label='Название категории:')
    author__name = CharFilter(lookup_expr='contains', label='Никнейм автора содержит:')
    available = BooleanFilter(field_name='available', label='Активна:')
    tag = CharFilter(lookup_expr='contains', label='Тэг содержит:')
    created_on = DateFromToRangeFilter(widget=RangeWidget(attrs={'placeholder': 'ДД.ММ.ГГГГ'}),
                                       label=('Дата создания (введите начальную и конечную дату в '
                                              'указанном формате):'))

    class Meta:
        model = Post
        fields = ['title', 'category__name', 'author__name', 'available', 'tag', 'created_on', ]


class UserFilter(FilterSet):
    """
    Filter for objects of the MyUser model by different criteria.
    """
    username = CharFilter(lookup_expr='contains', label='Никнейм содержит:')
    first_name = CharFilter(lookup_expr='contains', label='Имя содержит:')
    last_name = CharFilter(lookup_expr='contains', label='Фамилия содержит:')
    email = CharFilter(lookup_expr='contains', label='Email содержит:')
    is_active = BooleanFilter(field_name='is_active', label='Активен:')
    is_staff = BooleanFilter(field_name='is_staff', label='Является персоналом сайта:')
    is_superuser = BooleanFilter(field_name='is_superuser',
                                         label='Является суперпользователем:')
    social_network = BooleanFilter(field_name='social_network',
                                           label='Зарегистрирован через соцсеть:')
    score = RangeFilter(widget=RangeWidget(attrs={'placeholder': '0'}),
                                       label=('Счет (введите начальное '
                                              'и конечное значение):'))
    last_login = DateFromToRangeFilter(widget=RangeWidget(attrs={'placeholder': 'ДД.ММ.ГГГГ'}),
                                       label=('Последний заход на сайт (введите начальную и конечную дату в '
                                              'указанном формате):'))
    date_joined = DateFromToRangeFilter(widget=RangeWidget(attrs={'placeholder': 'ДД.ММ.ГГГГ'}),
                                       label=('Дата регистрации (введите начальную и конечную дату в '
                                              'указанном формате):'))

    class Meta:
        model = MyUser
        fields = ['username', 'first_name', 'last_name', 'email',
                  'social_network', 'is_active', 'is_staff', 'is_superuser',
                  'score', 'last_login', 'date_joined', ]
