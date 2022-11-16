"""
Contains serializers of models for the API of the project.
"""

from rest_framework import serializers
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer

from posts.models import Post
from questions.models import QuestionCategory, Question
from users.models import MyUser


class QuestionCategorySerializer(HyperlinkedModelSerializer):
    """Serializer for QuestionCategory objects."""
    class Meta:
        model = QuestionCategory
        fields = ('id', 'name', 'description', 'available')

    def to_representation(self, instance):
        """
        Adds the number of posts and questions in each category to the output.
        """
        representation = super().to_representation(instance)
        representation['posts'] = instance.post_set.count()
        representation['questions'] = instance.question_set.count()
        return representation


class QuestionSerializer(ModelSerializer):
    """Serializer for Question objects."""
    is_active = serializers.BooleanField(source='available')

    class Meta:
        model = Question
        exclude = ('author', 'available',)

    def validate(self, data):
        """
        Validating the presence of the correct answer among the suggested
        options when creating a new question.
        """
        if data['right_answer'] not in [data['answer_01'], data['answer_02'],
                                        data['answer_03'], data['answer_04']]:
            raise serializers.ValidationError('Among the answer options, there is '
                                              'no one that you indicated as correct!')
        return data


class PostSerializer(ModelSerializer):
    """Serializer for Post objects."""
    is_active = serializers.BooleanField(source='available')

    class Meta:
        model = Post
        exclude = ('author', 'available',)


class UserSerializer(ModelSerializer):
    """Serializer for MyUser objects."""
    class Meta:
        model = MyUser
        exclude = ('activation_key', 'activation_key_created',
                   'info', 'password', 'groups', 'user_permissions', )
        read_only_fields = ('last_login', 'social_network', 'date_joined', )
