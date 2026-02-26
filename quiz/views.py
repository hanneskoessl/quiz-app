from django.http import HttpResponse
from django.shortcuts import render

from .models import Question, Option

def index(request):
    """The home page for Quiz."""
    return render(request, "quiz/index.html")

def quiz(request):
    """Shows a quiz."""
    questions = Question.objects.prefetch_related("options")
    context = {'questions': questions}
    return render(request, 'quiz/quiz.html', context)

def results(request):
    """Quiz results."""
    return HttpResponse("Quiz results (not implemented yet)")