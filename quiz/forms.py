from django import forms

from .models import Quiz

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


        
    