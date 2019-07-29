from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import authentication,generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from main.permissions import NormalUserGetOnly
from rest_framework import filters
from rest_framework.settings import api_settings
from main.serializers import CommentSerializer,VoterSerializer, QVoterSerializer, QuestionSerializer, AnswerSerializer,TagsSerializer
# Create your views here.
from main.models import QVoter,Question,Voter,Comment,Answer,Tag
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.db import IntegrityError
from authemail.serializers import UserSerializer
# from django.views.decorators.http import va
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.utils.translation import gettext as _

# class StandardResultsSetPagination(PageNumberPagination):
#     page_size = 1
#     page_size_query_param = 'page_size'
#     max_page_size = 1


class QuestionViewSet(viewsets.ModelViewSet):
    permission_classes = (NormalUserGetOnly,)
    serializer_class = QuestionSerializer
    http_method_names = ['get', 'post', 'put', 'head']
    queryset = Question.objects.all()

    def perform_create(self, serializer):
        a = serializer.validated_data['question_text']
        print(a)
        serializer.save(user=self.request.user)

    # Cache requested url for each user for 2 hours
    @method_decorator(cache_page(60*60*2))
    @method_decorator(vary_on_cookie)
    def list(self, request, *args, **kwargs):
        user = self.request.user
        queryset = Question.objects.all()
        question = self.request.query_params.get('question', None)
        tag_name = self.request.query_params.get('question', None)
        if question is not None:
            queryset = queryset.filter(id=question)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = QuestionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = QuestionSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




    # def get_queryset(self):
    #     user = self.request.user
    #     queryset = Question.objects.all()
    #     question = self.request.query_params.get('question', None)
    #     if question is not None:
    #         queryset = queryset.filter(id=question)
    #     return queryset

    def update(self, request, *args, **kwargs):
        user = self.request.user
        object = self.get_object()
        if user == object.user:
            return super(QuestionViewSet, self).update(request, *args, **kwargs)
        content = {'detail': 'User do not have access to change the fields.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)


class AnswerViewSet(viewsets.ModelViewSet):
    # authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (NormalUserGetOnly,)
    serializer_class = AnswerSerializer
    http_method_names = ['post', 'put', 'head','get']
    queryset = Answer.objects.all()

    def perform_create(self, serializer):
        a=serializer.validated_data['answer_text']
        print(a)
        serializer.save(user=self.request.user)
    # Cache requested url for each user for 2 hours
    @method_decorator(cache_page(60*60*2))
    @method_decorator(vary_on_cookie)
    def list(self, request, *args, **kwargs):
        queryset = Answer.objects.all()
        question = self.request.query_params.get('question', None)
        answer = self.request.query_params.get('answer', None)
        if question is not None:
            queryset = queryset.filter(question=question)
        if answer is not None:
            queryset = queryset.filter(id=answer)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = AnswerSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = AnswerSerializer(queryset, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)



    def update(self, request, *args, **kwargs):
        user = self.request.user
        object = self.get_object()
        if user == object.user:
            return super(AnswerViewSet, self).update(request, *args, **kwargs)
        content = {'detail': 'User do not have access to change the fields.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)



class CommentViewset(viewsets.ModelViewSet):
    permission_classes = (NormalUserGetOnly,)
    serializer_class = CommentSerializer
    http_method_names = ['post', 'put', 'get']

    def perform_create(self, serializer):
        a=serializer.validated_data['comment_text']
        print(a)
        serializer.save(user=self.request.user)

    def get_queryset(self):
        user = self.request.user
        queryset = Comment.objects.all()
        question = self.request.query_params.get('question', None)
        answer = self.request.query_params.get('answer', None)
        comment= self.request.query_params.get('comment', None)
        if question is not None:
            queryset = queryset.filter(answer__question=question)
        if answer is not None:
            queryset = queryset.filter(answer=answer)
        if comment is not None:
            queryset=queryset.filter(id =comment)
        return queryset

    def update(self, request, *args, **kwargs):
        user = self.request.user
        organization_object = self.get_object()
        if user == organization_object.user:
            return super(CommentViewset, self).update(request, *args, **kwargs)
        content = {'detail': 'User do not have access to change the fields.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)



class QvoteView(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    serializer_class = QVoterSerializer
    def post(self, request, format=None):
        serializer = QVoterSerializer(data=request.data)
        if serializer.is_valid():
            question = serializer.data['question']
            question_obj = QVoter.objects.filter(question=question, user=request.user)
            question = Question.objects.get(id=question)

            if question.user== request.user:
                content = {'detail': 'You cannot vote your own question.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            if len(question_obj) == 0:
                a = QVoter.objects.create_qvoter(question=question, user=request.user)
                vote = question.question_votes
                question.question_votes=vote+1
                question.save()
                return Response({'question_vote':question.question_votes},status=status.HTTP_200_OK)
            else:
                question_obj.delete()
                vote = question.question_votes
                question.question_votes = vote-1
                question.save()
                return Response({'question_vote':question.question_votes})

        #
        # question_obj = QVoter.objects.filter(question=question,user=request_user)



class AvoteView(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    serializer_class = VoterSerializer
    def post(self, request, format=None):
        serializer = VoterSerializer(data=request.data)
        if serializer.is_valid():
            answer = serializer.data['answer']
            answer_obj = Voter.objects.filter(answer=answer, user=request.user)
            answer = Answer.objects.get(id=answer)

            if answer.user== request.user:
                content = {'detail': 'You cannot vote your own answer.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            if len(answer_obj) == 0:
                a = Voter.objects.create_qvoter(answer=answer, user=request.user)
                vote = answer.answer_votes
                answer.answer_votes=vote+1
                answer.save()
                return Response({'answer_vote':answer.answer_votes},status=status.HTTP_200_OK)
            else:
                answer_obj.delete()
                vote = answer.answer_votes
                answer.answer_votes = vote-1
                answer.save()
                return Response({'answer_vote':answer.answer_votes}, status=status.HTTP_200_OK)

# class Search(generics.ListAPIView):
#     permission_classes = (NormalUserGetOnly,)
#     queryset = Question.objects.all()
#     serializer_class = QuestionSerializer
#     filter_backends = [filters.SearchFilter]
#     search_fields = ['question_text']

class Talash(APIView):
    permission_classes = (NormalUserGetOnly,)
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    # Cache requested url for each user for 2 hours
    @method_decorator(cache_page(60*60*2))
    def get(self, request, format=None):

        words = self.request.query_params.get('words')
        if words is not None:
            print("nepal")
            question = Question.objects.filter(question_text__icontains=words)
            tag = Tag.objects.filter(tagname__icontains=words).values_list('question', flat=True)
            question_from_tag = Question.objects.all().filter(id__in=tag)
            answer = Answer.objects.filter(answer_text__icontains=words).values_list('question', flat=True)
            question_from_answer=Question.objects.all().filter(id__in=answer)
            search_obj = (question | question_from_tag |question_from_answer).distinct()
            page = self.paginate_queryset(search_obj)
            if page is not None:
                serializer = QuestionSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = QuestionSerializer(search_obj, read_only=True, many=True, required=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        content = {'detail': 'Search field is empty.'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object for the given output data.
        """
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

class TagViewSet(viewsets.ModelViewSet):
    permission_classes = (NormalUserGetOnly,)
    serializer_class = TagsSerializer
    http_method_names = ['get','head']
    def get_queryset(self):
        user = self.request.user
        queryset = Tag.objects.all()
        tag_name = self.request.query_params.get('tagname', None)
        if tag_name is not None:
            queryset = queryset.filter(tagname=tag_name)
        return queryset

    # def update(self, request, *args, **kwargs):
    #     user = self.request.user
    #     tag_object = self.get_object()
    #     if user == tag_object.user:
    #         return super(TagViewSet, self).update(request, *args, **kwargs)
    #     content = {'detail': 'User do not have access to change the fields.'}
    #     return Response(content, status=status.HTTP_400_BAD_REQUEST)


class TagApiView(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    def post(self, request, format=None):
        tag_name = request.data['tagname']
        question_id = request.data['question']
        tag, created = Tag.objects.get_or_create(tagname=tag_name)
        try:
            tag.question.add(question_id)
        except IntegrityError as e:
            content = {'detail': 'Question is aleready added on tag'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        question = Question.objects.get(id=question_id)
        return Response(QuestionSerializer(question).data, status=status.HTTP_200_OK)

