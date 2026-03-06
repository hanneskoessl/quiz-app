from django import forms

from .models import Option, Question, Quiz

class QuizForm(forms.Form):

    def __init__(self, *args, **kwargs):
        questions = kwargs.pop("questions")
        super().__init__(*args, **kwargs)

        for question in questions:
            self.fields[f"question_{question.id}"] = forms.ModelMultipleChoiceField(
                queryset=question.options.all(),
                required=False,
                widget=forms.CheckboxSelectMultiple,
                label=question.question,     
            )


class NewQuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title']
        labels = {'title': ''}


class NewQuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question', 'difficulty']
        labels = {'question': '',
                  'difficulty': ''}
        

class NewOptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['text', 'is_correct']
        labels = {'text': '',
                  'is_correct': ''}
