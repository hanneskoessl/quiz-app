from django.shortcuts import render

def index(request):
    """The home page for Quiz."""
    return render(request, "quiz/index.html")