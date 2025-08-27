from django.urls import path
from . import views

urlpatterns = [
    path("", views.chat_view, name="chat"),      # home = chat page
    path("quizzes/", views.quizzes_view, name="quizzes"),
    path("alarm/", views.alarm_view, name="alarm"),
]
