from django.http import HttpResponse
from django.shortcuts import redirect, render

from .forms import QuizForm
from .models import Question, Quiz, Option

def index(request):
    """The home page for Quiz."""
    return render(request, "quiz/index.html")

def quizzes(request):
    """Lists all quizzes."""
    quizzes = Quiz.objects.all()
    context = {'quizzes': quizzes}
    return render(request, "quiz/quizzes.html", context)

def quiz(request, quiz_id):
    """Shows a quiz."""
    quiz = Quiz.objects.get(id=quiz_id)
    questions = quiz.questions.prefetch_related("options")
    
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