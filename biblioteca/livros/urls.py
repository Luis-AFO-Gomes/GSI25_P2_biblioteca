from django.urls import path
from . import views

app_name = 'livros'

urlpatterns = [

    path(
        '',
        views.HomeArvoresView.as_view(),
        name='home_arvores'
    ),

    path(
        'catalogo/',
        views.ListaArvoresView.as_view(),
        name='lista_arvores'
    ),

    path(
        'arvore/nova/',
        views.ArvoreCreateView.as_view(),
        name='criar_arvore'
    ),

    path(
        'arvore/<int:pk>/',
        views.ArvoreDetailView.as_view(),
        name='detalhe_arvore'
    ),

    path(
        'arvore/<int:pk>/editar/',
        views.ArvoreUpdateView.as_view(),
        name='editar_arvore'
    ),

    path(
        'arvore/<int:pk>/apagar/',
        views.ArvoreDeleteView.as_view(),
        name='apagar_arvore'
    ),

]
