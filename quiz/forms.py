from django import forms

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
            

    
        
    