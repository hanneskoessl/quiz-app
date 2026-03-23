from django import forms

from .models import Option, Question, Quiz

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
    class Meta:
        model = Quiz
        fields = ['title', 'explanation']
        labels = {'title': '',
                  'explanation': ''}


class NewQuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question', 'difficulty']
        labels = {'question': '',
                  'difficulty': ''}
        

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
        labels = {'text': '',
                  'is_correct': ''}
