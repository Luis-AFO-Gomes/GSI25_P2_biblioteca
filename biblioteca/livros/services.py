from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError
from django.http import Http404

from .models import Livro


class LivroService:
    """Business-facing access layer for Livro operations."""

    @staticmethod
    def listar():
        try:
            return Livro.objects.select_related('editora').all()
        except DatabaseError as exc:
            raise Http404('Nao foi possivel obter a lista de livros.') from exc

    @staticmethod
    def obter_por_isbn(isbn):
        try:
            return Livro.objects.select_related('editora').get(isbn=isbn)
        except ObjectDoesNotExist as exc:
            raise Http404('Livro nao encontrado.') from exc
        except DatabaseError as exc:
            raise Http404('Nao foi possivel obter os dados do livro.') from exc

    @staticmethod
    def apagar(livro):
        try:
            livro.delete()
        except DatabaseError as exc:
            raise Http404('Nao foi possivel apagar o livro.') from exc
