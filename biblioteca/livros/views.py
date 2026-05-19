from django.shortcuts import render

def home_livros(request):
     return render(request, 'livros/home.html', {'title': 'Home', 'request': request})

#def home_livros(request):
#     return render(request, 'livros/home.html', {'title': 'Home', 'nome': 'World', 'request': request})

#def home_livros(request,nome='World'):
#    return render(request, 'livros/home.html', {'title': 'Home', 'nome': nome, 'request': request})