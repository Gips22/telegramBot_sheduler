from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect

def index(request):
    return HttpResponse('Страница приложения women.')

def categories(request, catid):
    if request.POST:
        print(request.GET)
    return HttpResponse(f"<h1>Статьи по категориям</h1><p>{catid} Хaй</p>")

def archive(request, year):
    if int(year) > 2020:
        return redirect('home', permanent=True)
    return HttpResponse(f"<h1>Архив по годам</h1><p>{year}</p>")

def pageNotFound(request, exception):
    return HttpResponseNotFound(f'<h1>Страница не найдена</h1>')