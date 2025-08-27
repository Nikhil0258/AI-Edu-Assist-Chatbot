from django.urls import path
from . import views

urlpatterns = [
    path('', views.edu_assist_view, name='edu_assist'),
    path('quizzes/', views.quizzes_view, name='quizzes'),
    path('quizzes/', views.quizzes_view, name='quiz_submit_url'),
]
