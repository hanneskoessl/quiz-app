from django.http import HttpResponse
from django.shortcuts import redirect, render

from .forms import QuizForm
from .models import Question, Option

def index(request):
    """The home page for Quiz."""
    return render(request, "quiz/index.html")

def quiz(request):
    """Shows a quiz."""
    questions = Question.objects.prefetch_related("options")
    
    if request.method == "POST":
        form = QuizForm(request.POST, questions=questions)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            print(cleaned_data)
            return redirect("quiz:results")        
    else:
        form = QuizForm(questions=questions)

    context = {'form': form}
    return render(request, 'quiz/quiz.html', context)

def results(request):
    """Quiz results."""
    return HttpResponse("Quiz results (not implemented yet)")