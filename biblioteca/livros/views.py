from django.shortcuts import render

def home_livros(request):
     return render(request, 'livros/home.html', {'title': 'Home', 'request': request})

#def home_livros(request):
#     return render(request, 'livros/home.html', {'title': 'Home', 'nome': 'World', 'request': request})

#def home_livros(request,nome='World'):
#    return render(request, 'livros/home.html', {'title': 'Home', 'nome': nome, 'request': request})
# uso: http://localhost:8000/livros/ ou http://localhost:8000/livros/«nome»
# 1. reverte para default: nome = 'World'
# 2. Apresenta o nome passado na URL: nome = '«nome»
# - é necessário confirmar que existe um path correspondente (com parâmetro) em livros/urls.py