from django.db import models
from authemail.models import EmailAbstractUser, EmailUserManager
from django.conf import settings
# Create your models here.
# Create your models here.
class StackUser(EmailAbstractUser):
    # Custom fields
    date_of_birth = models.DateField(null=True,
                                     blank=True)
    website = models.URLField(null=True,blank=True)
    address = models.CharField(max_length=100, blank=True, null=True)

    objects = EmailUserManager()


    def reputation(self):
        question_obj = Question.objects.all().filter(user=self)
        answer_obj = Answer.objects.all().filter(user=self)
        q_votes=0
        a_votes=0
        if question_obj:
            for que in question_obj:
                q_votes = q_votes+que.question_votes
        if answer_obj:
            for ans in answer_obj:
                a_votes = a_votes + ans.answer_votes
        total_votes = a_votes+q_votes
        rep = round(total_votes/1)
        return rep






class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField(auto_now_add=True)
    # tags = models.ManyToManyField(Tag)
    question_votes = models.IntegerField(null=True, blank=True, default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    closed = models.BooleanField(default=False)

    def __str__(self):
        return self.question_text


class Answer(models.Model):
    question = models.ForeignKey(Question,related_name='answer')
    answer_text = models.TextField(default=None, null=True, blank=True)
    answer_votes = models.IntegerField(default=0)
    pub_date = models.DateTimeField(auto_now_add=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.answer_text




class AVoterManager(models.Manager):
    def create_qvoter(
            self,
            user,
            answer,
    ):
        voter = self.create(answer=answer, user=user)
        return voter

class Voter(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    answer = models.ForeignKey(Answer)
    objects = AVoterManager()

class QvoterManager(models.Manager):
    def create_qvoter(
            self,
            question,
            user,
           ):
        qvoter = self.create(question=question, user=user)
        return qvoter


class QVoter(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    question = models.ForeignKey(Question)
    objects = QvoterManager()


class QvoterManager(models.Manager):
    def create_qvoter(
            self,
            question,
            user,
    ):
        qvoter = self.create(question=question, user=user)
        return qvoter



class Comment(models.Model):
    answer = models.ForeignKey(Answer)
    comment_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField(auto_now_add=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.comment_text

class Tag(models.Model):
    question = models.ManyToManyField(
        Question,
        related_name="tags"
    )
    tagname = models.TextField()

    def get_question(self):
        return ",".join([str(p) for p in self.question.all()])

    def __str__(self):
        return self.tagname
