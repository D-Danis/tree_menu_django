from django.shortcuts import render

def home(request):
    return render(request, 'menu/bar/home.html')

def about(request):
    return render(request, 'menu/bar/about.html')