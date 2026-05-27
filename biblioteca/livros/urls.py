from django.urls import path
from . import views

app_name = 'livros'
urlpatterns = [
    path('', views.HomeLivrosView.as_view(), name='home_livros'),
    path('catalogo/', views.ListaLivrosView.as_view(), name='lista_livros'),
    path('livro/novo/', views.LivroCreateView.as_view(), name='criar_livro'),
    path('livro/<str:isbn>/', views.LivroDetailView.as_view(), name='detalhe_livro'),
    path('livro/<str:isbn>/editar/', views.LivroUpdateView.as_view(), name='editar_livro'),
    path('livro/<str:isbn>/apagar/', views.LivroDeleteView.as_view(), name='apagar_livro'),
]
