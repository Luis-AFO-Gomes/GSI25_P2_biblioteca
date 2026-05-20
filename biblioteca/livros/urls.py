from django.urls import path
from . import views

app_name = 'livros'
urlpatterns = [
    path('', views.home_livros, name='home_livros'),
#    path('<str:nome>/', views.home_livros, name='home_livros_nome'),
    path('catalogo/', views.lista_livros, name='lista_livros'),
]