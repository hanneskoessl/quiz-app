"""Define URL patterns for quiz."""

from django.urls import path

from . import views

app_name = "quiz"
urlpatterns = [
    # Home page
    path("", views.index, name="index"),
    # Page that shows a quiz.
    path("quizzes/", views.quizzes, name="quizzes"),
    path("edit_quizzes/", views.edit_quizzes, name="edit_quizzes"),
    path("quiz/<int:quiz_id>/", views.quiz, name="quiz"),
    path("results/<int:attempt_id>/", views.results, name="results"),
    path("new_quiz/", views.new_quiz, name="new_quiz"),
    path("new_question/<int:quiz_id>/", views.new_question, name="new_question"),
    path("new_option/<int:quiz_id>/<int:question_id>/", views.new_option, name="new_option"),
    path("quizzes/delete_quiz/<int:quiz_id>/", views.delete_quiz, name="delete_quiz"),
    path("delete_question/<int:quiz_id>/<int:question_id>/", views.delete_question, name="delete_question"),
    path("remove_question/<int:quiz_id>/<int:question_id>/", views.remove_question, name="remove_question"),
    path("delete_option/<int:quiz_id>/<int:question_id>/<int:option_id>/", views.delete_option, name="delete_option"),
    path("edit_quiz/<int:quiz_id>/", views.edit_quiz, name="edit_quiz"),
    path("attempts/", views.attempts, name="attempts"),
    path("quiz/<int:quiz_id>/stats/", views.quiz_stats, name="quiz_stats"),
]