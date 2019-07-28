from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from main.models import Question, QVoter, Answer, Voter, Comment,Tag
from authemail.serializers import UserSerializer
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth import get_user_model

class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("tagname",
                'question')



class QuestionSerializer(serializers.ModelSerializer):
    answer = serializers.StringRelatedField(many=True)
    tags = serializers.SlugRelatedField(many=True,slug_field="tagname",queryset=Tag.objects.all(),allow_null=Tag)
    class Meta:
        model = Question
        fields = (
            'id',
            'question_text',
            'pub_date',
            'question_votes',
            'user',
            'closed',
            'tags',
            'answer'
        )




class QuestionReperesent(serializers.BaseSerializer):

    def to_representation(self, obj):
        return {
            'id': obj.id,
            'question_text': obj.question_text,
            'question_votes': obj.question_votes,
            'user':obj.user.id
        }

    def to_internal_value(self, data):
        try:
            print(data)
            question = Question.objects.get(id=data)
            return question
        except KeyError:
            raise serializers.ValidationError(
                'id is a required field.'
            )

class AnswerSerializer(serializers.ModelSerializer):
    question=QuestionReperesent(required=False)
    class Meta:
        model = Answer
        fields=(
            'id',
            'user',
            'answer_text',
            'answer_votes',
            'pub_date',
            'question',

        )

class VoterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voter
        fields = (
            'id',
            'user',
            'answer'
        )

class QVoterSerializer(serializers.ModelSerializer):
    class Meta:
        model = QVoter
        fields = (
            'id',
            'user',
            'question'
        )
    def create(self, validated_data):
        request_user = self.context['request'].user
        validated_data['user'] = request_user
        question = validated_data.get('question', None)
        question_obj = QVoter.objects.filter(question=question,user=request_user)
        if len(question_obj) > 0:
            raise serializers.ValidationError(
                'You have alreaday voted')
        else:
            return QVoter.objects.create(**validated_data)




class AnswerReperesent(serializers.BaseSerializer):

    def to_representation(self, obj):
        return {
            'id': obj.id,
            'answer_text': obj.answer_text,
            'answer_votes': obj.answer_votes,
            'question':obj.question.question_text
        }

    def to_internal_value(self, data):
        try:
            answer = Answer.objects.get(id=data)
            return answer
        except KeyError:
            raise serializers.ValidationError(
                'id is a required field.'
            )



class CommentSerializer(serializers.ModelSerializer):
    answer = AnswerReperesent(required=False)
    class Meta:
        model = Comment
        fields = (
            'id',
            'user',
            'answer',
            'comment_text',
            'pub_date',
        )

