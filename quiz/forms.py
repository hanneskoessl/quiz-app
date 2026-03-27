from django import forms

from .models import Option, Question, Quiz, Visibility

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

    class Meta:
        model = Quiz
        fields = ['title', 'explanation']
        labels = {'title': '',
                  'explanation': ''}
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance:
            self.fields["link_sharing"].initial = (
                self.instance.visibility == Visibility.UNLISTED
            )

    def save(self, commit=True):
        quiz = super().save(commit=False)

        if self.cleaned_data.get("link_sharing"):
            quiz.visibility = Visibility.UNLISTED
        else:
            quiz.visibility = Visibility.PRIVATE

        if commit:
            quiz.save()
            self.save_m2m()

        return quiz


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
