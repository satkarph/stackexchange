from django.contrib import admin
from django.contrib.auth import get_user_model
# Register your models here.
from authemail.admin import EmailUserAdmin
from main.models import Question,Answer,QVoter,Voter, Comment, Tag
class StackUserAdmin(EmailUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'date_of_birth', 'website', 'address')}),
        ('Permissions', {'fields': ('is_active', 'is_staff',
                                    'is_superuser', 'is_verified',
                                    'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Custom info', {'fields': ('date_of_birth',)}),
    )

admin.site.register(get_user_model(), StackUserAdmin)


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('user', 'question_text', 'pub_date', 'question_votes', 'closed')

admin.site.register(Question,QuestionAdmin)


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'user', 'answer_text', 'answer_votes', 'pub_date')
admin.site.register(Answer,AnswerAdmin)


class QvoterAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'question')
admin.site.register(QVoter,QvoterAdmin)


class VoterAdmin(admin.ModelAdmin):
    list_display = ('user', 'answer')
admin.site.register(Voter,VoterAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'answer', 'comment_text', 'pub_date' )
admin.site.register(Comment,CommentAdmin)

class Tagadmin(admin.ModelAdmin):
    list_display = ('question', 'tagname')
    def question(self, obj):
        return "\n".join([a.id for a in obj.question.all()])

admin.site.register(Tag,Tagadmin)





