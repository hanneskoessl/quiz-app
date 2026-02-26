"""Define URL patterns for quiz."""

from django.urls import path

from . import views

app_name = "quiz"
urlpatterns = [
    # Home page
    path("", views.index, name="index"),
    # Page that shows a quiz.
    path("quiz/", views.quiz, name="quiz"),
    path("results/", views.results, name="results"),
]