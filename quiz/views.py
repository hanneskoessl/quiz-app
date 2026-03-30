from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Prefetch, Q
from django.db.models import Avg, Max, Count
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse

from .forms import QuizForm, NewQuizForm, NewQuestionForm, NewOptionForm, AddExistingQuestionForm
from .models import Question, Quiz, QuizAttempt, Option, Visibility
from .utils import can_access_quiz

def index(request):
    """The home page for Quiz."""
    return render(request, "quiz/index.html")

@login_required
def quizzes(request):
    """Lists all quizzes."""
    quizzes = Quiz.objects.filter(
        Q(owner=request.user) |
        Q(allowed_users=request.user) & ~Q(visibility="private")
    ).distinct()
    context = {'quizzes': quizzes}
    return render(request, "quiz/quizzes.html", context)

@login_required
def edit_quizzes(request):
    """Lists all quizzes."""
    quizzes = Quiz.objects.filter(owner=request.user)
    context = {'quizzes': quizzes}
    return render(request, "quiz/edit_quizzes.html", context)

@transaction.atomic
def quiz(request, quiz_id):
    """Shows a quiz."""
    token = request.GET.get("token")

    quiz = get_object_or_404(
        Quiz.objects.prefetch_related("questions__options"),
        id=quiz_id
    )

    if not can_access_quiz(request.user, quiz, token):
        raise Http404()

#    if quiz.owner != request.user:
#        raise Http404
    
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
                owner=request.user if request.user.is_authenticated else None,
            )

            snapshot = []

            for question in questions:
                                
                selected_ids = set(
                    map(int, form.cleaned_data.get(f"question_{question.id}", []))
                )

                correct_ids = {
                    option.id
                    for option in question.options.all()
                    if option.is_correct
                }
                
                options_data = []

                for option in question.options.all():
                    options_data.append(
                        {
                            "id": option.id,
                            "text": option.text,
                            "is_correct": option.is_correct,
                            "selected": option.id in selected_ids,
                        }
                    )

                snapshot.append(
                    {
                        "question_id": question.id,
                        "text": question.question,
                        "options": options_data,
                    }
                )

                is_question_correct = selected_ids == correct_ids

                if is_question_correct:
                    score += 1

            attempt.snapshot = snapshot
            attempt.score = score
            attempt.save()

            url = reverse("quiz:results", args=[attempt.id])

            
            if not request.user.is_authenticated:
                token = attempt.token
                url += f"?token={token}"

            return redirect(url)        
    else:
        form = QuizForm(questions=quiz.questions.all())

    context = {'quiz': quiz,
               'form': form,
               }
    return render(request, 'quiz/quiz.html', context)

def results(request, attempt_id):
    """Quiz results."""
    token = request.GET.get("token")

    attempt = get_object_or_404(
        QuizAttempt,
        id=attempt_id
    )

    quiz = attempt.quiz

    if not (
        attempt.owner == request.user or
        (token and str(attempt.token) == str(token))
    ):
        raise Http404()

    percentage = round((attempt.score / attempt.total) * 100, 1)

    share_link = attempt.get_share_link(request)
    
    context = {'quiz': quiz,
               'attempt': attempt,
               'percentage': percentage,
               'share_link': share_link,
               }
    return render(request, 'quiz/results.html', context)

@login_required
def new_quiz(request):
    """Add a new quiz."""
    if request.method != 'POST':
        form = NewQuizForm()
    else:
        form = NewQuizForm(data=request.POST)
        if form.is_valid():
            new_quiz = form.save(commit=False)
            new_quiz.owner = request.user
            new_quiz.save()
            form.save_m2m()
            user = form.cleaned_data.get("share_with_user")
            if user:
                new_quiz.allowed_users.add(user)
                if new_quiz.visibility != Visibility.UNLISTED:
                    new_quiz.visibility = Visibility.SHARED
                    new_quiz.save()
            return redirect("quiz:new_question", quiz_id=form.instance.id)
    
    context = {'form': form}
    return render(request, 'quiz/new_quiz.html', context)

@login_required
def edit_quiz(request, quiz_id):
    """Edit a quiz."""

    quiz = get_object_or_404(
        Quiz, 
        id=quiz_id
    )

    if quiz.owner != request.user:
        raise Http404

    share_link = None
    if quiz.is_link_sharing_enabled():
        share_link = quiz.get_share_link(request)
    
    if request.method == "POST":
        form = NewQuizForm(request.POST, instance=quiz)

        if form.is_valid():
            form.save()
            return redirect("quiz:edit_quiz", quiz_id=quiz_id)
    else:
        form = NewQuizForm(instance=quiz)

    context = {
        "quiz": quiz,
        "form": form,
        "share_link": share_link,
    }

    return render(request, "quiz/edit_quiz.html", context)

@login_required
def new_question(request, quiz_id):
    """Add a new question."""
    quiz = get_object_or_404(
        Quiz, 
        id=quiz_id
    )

    if quiz.owner != request.user:
        raise Http404

    questions = quiz.questions.prefetch_related("options")

    if request.method == "POST":

        if "create_question" in request.POST:
            new_form = NewQuestionForm(request.POST)

            if new_form.is_valid():
                new_question = new_form.save(commit=False)
                new_question.owner = request.user
                new_question.save()
                quiz.questions.add(new_question)

                return redirect("quiz:new_question", quiz_id=quiz_id)

        elif "add_existing" in request.POST:
            existing_form = AddExistingQuestionForm(request.POST, user=request.user)

            if existing_form.is_valid():
                question = existing_form.cleaned_data["question"]

                if question.owner != request.user:
                    raise Http404

                quiz.questions.add(question)

                return redirect("quiz:new_question", quiz_id=quiz_id)

    else:
        new_form = NewQuestionForm()
        existing_form = AddExistingQuestionForm(user=request.user)

    context = {
        "quiz": quiz,
        "questions": questions,
        "new_form": new_form,
        "existing_form": existing_form,
    }

    return render(request, "quiz/new_question.html", context)

@login_required
def new_option(request, quiz_id, question_id):
    """Add a new question."""
    question = get_object_or_404(
        Question,
        id=question_id
    )

    if question.owner != request.user:
        raise Http404

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

@login_required
def delete_quiz(request, quiz_id):
    """Delete a quiz."""
    quiz = get_object_or_404(
        Quiz,
        id=quiz_id
    )

    if quiz.owner != request.user:
        raise Http404

    if request.method == 'POST':
        quiz.delete()
        return redirect ('quiz:edit_quizzes')

    return redirect ('quiz:edit_quizzes')

@login_required
def delete_question(request, quiz_id, question_id):
    """Delete a question."""
    question = get_object_or_404(
        Question,
        id=question_id
    )

    if question.owner != request.user:
        raise Http404

    if request.method == 'POST':
        question.delete()
        return redirect ('quiz:new_question', quiz_id=quiz_id)

    return redirect ('quiz:new_question', quiz_id=quiz_id)

@login_required
def remove_question(request, quiz_id, question_id):
    """Remove Question from Quiz."""
    quiz = get_object_or_404(
        Quiz,
        id=quiz_id
    )

    if quiz.owner != request.user:
        raise Http404

    question = get_object_or_404(
        Question,
        id=question_id
    )

    if request.method == 'POST':
        if quiz.questions.filter(id=question_id).exists():
            quiz.questions.remove(question)
        return redirect ('quiz:new_question', quiz_id=quiz_id)
    
    return redirect ('quiz:new_question', quiz_id=quiz_id)

@login_required
def delete_option(request, quiz_id, question_id, option_id):
    """Delete an option."""
    option = get_object_or_404(
        Option,
        id=option_id
    )

    question = option.question

    if question.owner != request.user:
        raise Http404

    if request.method == 'POST':
        option.delete()
        return redirect ('quiz:new_option', quiz_id=quiz_id, question_id=question_id)

    return redirect ('quiz:new_option', quiz_id=quiz_id, question_id=question_id)

@login_required
def attempts(request):
    quizzes = Quiz.objects.filter(
        Q(owner=request.user) |
        Q(allowed_users=request.user) & ~Q(visibility="private")
    ).distinct().prefetch_related(
        Prefetch(
            "attempts",
            queryset=QuizAttempt.objects.filter(owner=request.user),
        )
    )

    context = {'quizzes': quizzes}
    return render(request, "quiz/attempt.html", context)

def quiz_stats(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    attempts = QuizAttempt.objects.filter(
        Q(quiz=quiz) & Q(owner=request.user)
    ).order_by("created_at")

    stats = attempts.aggregate(
        total_attempts=Count("id"),
        avg_score=Avg("score"),
        best_score=Max("score"),
    )

    scores = list(attempts.values_list("score", flat=True))
    dates = [a.created_at.strftime("%d.%m") for a in attempts]

    context = {
        "quiz": quiz,
        "stats": stats,
        "scores": scores,
        "dates": dates,
    }

    return render(request, "quiz/quiz_stats.html", context)