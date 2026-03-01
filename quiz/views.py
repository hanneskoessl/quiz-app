from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404

from .forms import QuizForm
from .models import Answer, Question, Quiz, QuizAttempt, Option

def index(request):
    """The home page for Quiz."""
    return render(request, "quiz/index.html")

def quizzes(request):
    """Lists all quizzes."""
    quizzes = Quiz.objects.all()
    context = {'quizzes': quizzes}
    return render(request, "quiz/quizzes.html", context)

@transaction.atomic
def quiz(request, quiz_id):
    """Shows a quiz."""
    quiz = get_object_or_404(
        Quiz.objects.prefetch_related("questions__options"),
        id=quiz_id
    )
    
    questions = quiz.questions.all()
    
    if request.method == "POST":
        form = QuizForm(request.POST, questions=questions)

        if form.is_valid():
            score = 0
            total = questions.count()

            print(form.cleaned_data)

            attempt = QuizAttempt.objects.create(
                quiz=quiz,
                score=0,
                total=total,
            )

            answers_to_create = []

            for question in questions:
                                
                selected_qs = form.cleaned_data.get(
                    f"question_{question.id}", 
                    question.options.none()
                )

                selected_ids = set(
                    selected_qs.values_list("id", flat=True)
                )

                correct_ids = set(
                    question.options
                    .filter(is_correct=True)
                    .values_list("id", flat=True)
                )
                
                is_question_correct = selected_ids == correct_ids

                if is_question_correct:
                    score += 1

                for option in selected_qs:
                    answers_to_create.append(
                        Answer(
                            attempt=attempt,
                            question=question,
                            option=option,
                            is_correct=option.is_correct,
                        )
                    )
                    
            Answer.objects.bulk_create(answers_to_create)

            attempt.score = score
            attempt.save()

            return redirect("quiz:results")        
    else:
        form = QuizForm(questions=quiz.questions.all())

    context = {'form': form}
    return render(request, 'quiz/quiz.html', context)

def results(request):
    """Quiz results."""
    return HttpResponse("Quiz results (not implemented yet)")