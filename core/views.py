"""Core views"""

from django.shortcuts import render


def about(request):
    """Responds with 'about' page"""
    return render(request, "about.html")

def codeofconduct(request):
    return render(request, "codeofconduct.html")