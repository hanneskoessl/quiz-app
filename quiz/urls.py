"""Define URL patterns for quiz."""

from django.urls import path

from . import views

app_name = "quiz"
urlpatterns = [
    # Home page
    path("", views.index, name="index"),
    # Page that shows a quiz.
    path("quizzes/", views.quizzes, name="quizzes"),
    path("quiz/<int:quiz_id>/", views.quiz, name="quiz"),
    path("results/<int:attempt_id>/", views.results, name="results"),
    path("new_quiz/", views.new_quiz, name="new_quiz"),
    path("new_question/<int:quiz_id>/", views.new_question, name="new_question"),
    path("new_option/<int:quiz_id>/<int:question_id>/", views.new_option, name="new_option"),
]