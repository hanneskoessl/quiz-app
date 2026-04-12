import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

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
    question = models.TextField()
    difficulty = models.PositiveSmallIntegerField(choices=Difficulty.choices)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.question[:50]


class Option(models.Model):
    """Answer option for a question."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class Visibility(models.TextChoices):
    PRIVATE = "private", "Private"
    UNLISTED = "unlisted", "Unlisted"
    SHARED = "shared", "Shared with users"


class Category(models.Model):
    """Quiz Category"""
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class QuizAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey("Quiz", on_delete=models.CASCADE)
    shared_at = models.DateTimeField(auto_now_add=True)
    shared_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="shared_given"
    )


class Quiz(models.Model):
    """Quiz"""
    title = models.CharField(max_length=200)
    explanation = models.TextField(blank=True)
    questions = models.ManyToManyField(Question, related_name="quizzes")
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quizzes"
    )

    visibility = models.CharField(
        max_length=10,
        choices=Visibility.choices,
        default=Visibility.PRIVATE
    )

    share_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    allowed_users = models.ManyToManyField(
        User,
        through="QuizAccess",
        through_fields=("quiz", "user"),
        blank=True,
        related_name="shared_quizzes"
    )

    def is_link_sharing_enabled(self):
        return self.visibility == Visibility.UNLISTED

    def get_share_link(self, request):
        if not self.is_link_sharing_enabled():
            return None
        
        url = reverse("quiz:quiz", args=[self.id])
        return request.build_absolute_uri(f"{url}?token={self.share_token}")

    def __str__(self):
        return self.title


class QuizAttempt(models.Model):
    """Quiz Attempt"""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    created_at = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField()
    total = models.IntegerField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    snapshot = models.JSONField(null=True, blank=True) 

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    def get_share_link(self, request):
        url = reverse("quiz:results", args=[self.id])
        return request.build_absolute_uri(f"{url}?token={self.token}")

    def __str__(self):
        return f"Attemp {self.id} - {self.score}/{self.total}" 