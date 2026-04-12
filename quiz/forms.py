from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Option, Question, Quiz, Visibility, Category, QuizAccess

class QuizForm(forms.Form):

    def __init__(self, *args, **kwargs):
        questions = kwargs.pop("questions")
        super().__init__(*args, **kwargs)

        for question in questions:
            options = list(question.options.all())

            self.fields[f"question_{question.id}"] = forms.MultipleChoiceField(
                required=False,
                choices=[(o.id, o.text) for o in options],
                widget=forms.CheckboxSelectMultiple,
                label=question.question,     
            )


class NewQuizForm(forms.ModelForm):
    link_sharing = forms.BooleanField(required=False, label="Linkfreigabe aktivieren")
    share_with_user = forms.CharField(
        required=False,
        label="Benutzer freigeben",
        help_text="Benutzernamen eingeben"
    )

    new_category = forms.CharField(
        required=False,
        label="Neue Kategorie",
        max_length=100
    )

    class Meta:
        model = Quiz
        fields = ['title', 'explanation', 'category']
        labels = {'title': 'Titel:',
                  'explanation': 'Erklärung:',
                  'category': 'Kategorie:'
                  }
        
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_user = user
        self.fields["link_sharing"].label_suffix = ""

        if self.instance:
            self.fields["link_sharing"].initial = (
                self.instance.visibility == Visibility.UNLISTED
            )

        if user:
            self.fields["category"].queryset = Category.objects.filter(owner=user)

    def clean_share_with_user(self):
        username = self.cleaned_data.get("share_with_user")
        
        if not username:
            return None

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise ValidationError("User existiert nicht")

        return user

    def save(self, commit=True):
        quiz = super().save(commit=False)

        if self.cleaned_data.get("link_sharing"):
            quiz.visibility = Visibility.UNLISTED

        if commit: 
            quiz.save() 
            self.save_m2m() 

            new_category_name = self.cleaned_data.get("new_category")
            selected_category = self.cleaned_data.get("category")

            if new_category_name:
                category, created = Category.objects.get_or_create(
                    name=new_category_name.strip(),
                    owner=self.request_user
                )
                quiz.category = category
            else:
                quiz.category = selected_category
            
            quiz.save()
            self.save_m2m()

        return quiz


class NewQuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question', 'difficulty']
        labels = {'question': 'Frage',
                  'difficulty': 'Schwerigkeit'}
        

class AddExistingQuestionForm(forms.Form):
    question = forms.ModelChoiceField(
        queryset=Question.objects.none(),
        label="Vorhandene Frage auswählen"
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['question'].queryset = Question.objects.filter(owner=user)
        

class NewOptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['text', 'is_correct']
        labels = {'text': 'Text',
                  'is_correct': 'Antwort ist richtig'}
