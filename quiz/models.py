from django.db import models
from django.core.exceptions import ValidationError
# Create your models here.

class Difficulty(models.IntegerChoices):
    """Possible difficulty level of the questions."""
    VERY_EASY = 1, "Very Easy"
    EASY = 2, "Easy"
    MEDIUM = 3, "Medium"
    HARD = 4, "Hard"
    VERY_HARD = 5, "Very Hard"


class Question(models.Model):
    """Question that can be used to create a quiz."""
    question = models.CharField(max_length=600)
    difficulty = models.PositiveSmallIntegerField(choices=Difficulty.choices)

    def __str__(self):
        return self.question


class Option(models.Model):
    """Answer option for a question."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class Quiz(models.Model):
    """Quiz"""
    title = models.CharField(max_length=200)
    questions = models.ManyToManyField(Question, related_name="quizzes")

    def __str__(self):
        return self.title


class QuizAttempt(models.Model):
    """Quiz Attempt"""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    created_at = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField()
    total = models.IntegerField()

    def __str__(self):
        return f"Attemp {self.id} - {self.score}/{self.total}"


class Answer(models.Model):
    """Quiz Answer"""
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question.question[:30]} - {self.option.text}"
    
