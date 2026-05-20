from django.shortcuts import render
from django.http import Http404
from django.shortcuts import get_object_or_404

from livros.models import Livro

def home_livros(request):
    livros = Livro.objects.all()
    return render(request, 'livros/home.html', {'title': 'Home', 'livros': livros, 'request': request})

#def home_livros(request):
#     return render(request, 'livros/home.html', {'title': 'Home', 'nome': 'World', 'request': request})

#def home_livros(request,nome='World'):
#    return render(request, 'livros/home.html', {'title': 'Home', 'nome': nome, 'request': request})

def lista_livros(request):
    livros = Livro.objects.all()  
    return render(request, 'livros/livros.html', {'livros': livros})