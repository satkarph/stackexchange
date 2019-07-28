"""stackexchange URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers
from main.views import QuestionViewSet,AnswerViewSet,CommentViewset,QvoteView,AvoteView,Talash,TagViewSet,TagApiView
router = routers.DefaultRouter()

router.register(r'comment', CommentViewset, 'comment')
router.register(r'question', QuestionViewSet, 'question')
router.register(r'answer', AnswerViewSet, 'answer')
router.register(r'tag', TagViewSet, 'tag')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    url(r'^api/accounts/', include('authemail.urls')),
    url(r'questionvote', QvoteView.as_view()),
    url(r'answervote', AvoteView.as_view()),
    # url(r'search', Search.as_view()),
    url(r'search', Talash.as_view()),
    url(r'tagquestion',TagApiView.as_view())


]
