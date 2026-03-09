from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404

from .forms import QuizForm, NewQuizForm, NewQuestionForm, NewOptionForm, AddExistingQuestionForm
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
                        )
                    )
                    
            Answer.objects.bulk_create(answers_to_create)

            attempt.score = score
            attempt.save()

            return redirect("quiz:results", attempt_id=attempt.id)        
    else:
        form = QuizForm(questions=quiz.questions.all())

    context = {'form': form}
    return render(request, 'quiz/quiz.html', context)

def results(request, attempt_id):
    """Quiz results."""
    attempt = get_object_or_404(
        QuizAttempt,
        id=attempt_id
    )

    quiz = attempt.quiz
    
    questions = quiz.questions.prefetch_related("options")
    
    selected_dict = {}

    for answer in attempt.answers.all():
        selected_dict.setdefault(answer.question_id, set()).add(answer.option_id)

    for question in questions:
        for option in question.options.all():
            option.selected = option.id in selected_dict.get(question.id, set())

    print(selected_dict)

    context = {'quiz': quiz,
               'questions': questions,
               'attempt': attempt,
               }
    return render(request, 'quiz/results.html', context)

def new_quiz(request):
    """Add a new quiz."""
    if request.method != 'POST':
        form = NewQuizForm()
    else:
        form = NewQuizForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("quiz:new_question", quiz_id=form.instance.id)
    
    context = {'form': form}
    return render(request, 'quiz/new_quiz.html', context)

def new_question(request, quiz_id):
    """Add a new question."""
    quiz = get_object_or_404(
        Quiz, 
        id=quiz_id
    )

    questions = quiz.questions.prefetch_related("options")

    if request.method == "POST":

        if "create_question" in request.POST:
            new_form = NewQuestionForm(request.POST)

            if new_form.is_valid():
                question = new_form.save()
                quiz.questions.add(question)

                return redirect("quiz:new_question", quiz_id=quiz_id)

        elif "add_existing" in request.POST:
            existing_form = AddExistingQuestionForm(request.POST)

            if existing_form.is_valid():
                question = existing_form.cleaned_data["question"]
                quiz.questions.add(question)

                return redirect("quiz:new_question", quiz_id=quiz_id)

    else:
        new_form = NewQuestionForm()
        existing_form = AddExistingQuestionForm()

    context = {
        "quiz": quiz,
        "questions": questions,
        "new_form": new_form,
        "existing_form": existing_form,
    }

    return render(request, "quiz/new_question.html", context)

def new_option(request, quiz_id, question_id):
    """Add a new question."""
    question = get_object_or_404(
        Question,
        id=question_id
    )

    if request.method != 'POST':
        form = NewOptionForm()
    else:
        form = NewOptionForm(data=request.POST)
        if form.is_valid():
            option = form.save(commit=False)
            option.question = question
            option.save()
    
            return redirect('quiz:new_option', quiz_id=quiz_id, question_id=question_id)
        
    context = {'quiz_id': quiz_id,
               'question': question,
               'form': form,
               }
    return render(request, 'quiz/new_option.html', context)

def delete_quiz(request, quiz_id):
    """Delete a quiz."""
    quiz = get_object_or_404(
        Quiz,
        id=quiz_id
    )

    if request.method == 'POST':
        quiz.delete()
        return redirect ('quiz:quizzes')

    return redirect ('quiz:quizzes')

def delete_question(request, quiz_id, question_id):
    """Delete a question."""
    question = get_object_or_404(
        Question,
        id=question_id
    )

    if request.method == 'POST':
        question.delete()
        return redirect ('quiz:new_question', quiz_id=quiz_id)

    return redirect ('quiz:new_question', quiz_id=quiz_id)

def delete_option(request, quiz_id, question_id, option_id):
    """Delete an option."""
    option = get_object_or_404(
        Option,
        id=option_id
    )

    if request.method == 'POST':
        option.delete()
        return redirect ('quiz:new_option', quiz_id=quiz_id, question_id=question_id)

    return redirect ('quiz:new_option', quiz_id=quiz_id, question_id=question_id)