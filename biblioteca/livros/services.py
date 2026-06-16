from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError
from django.http import Http404

from .models import Arvore


class ArvoreService:

    @staticmethod
    def listar():
        try:
            return Arvore.objects.all()

        except DatabaseError as exc:
            raise Http404(
                'Não foi possível obter a lista de árvores.'
            ) from exc

    @staticmethod
    def obter_por_id(id):
        try:
            return Arvore.objects.get(id=id)

        except ObjectDoesNotExist as exc:
            raise Http404(
                'Árvore não encontrada.'
            ) from exc

        except DatabaseError as exc:
            raise Http404(
                'Não foi possível obter os dados da árvore.'
            ) from exc

    @staticmethod
    def apagar(arvore):
        try:
            arvore.delete()

        except DatabaseError as exc:
            raise Http404(
                'Não foi possível apagar a árvore.'
            ) from exc
