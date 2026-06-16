from django import forms

from .models import Arvore


class ArvoreForm(forms.ModelForm):

    class Meta:

        model = Arvore

        fields = [
            'nome',
            'tipo',
            'altura',
            'preco',
            'stock',
            'pais_origem'
        ]

        labels = {
            'nome': 'Nome',
            'tipo': 'Tipo',
            'altura': 'Altura',
            'preco': 'Preço (€)',
            'stock': 'Stock',
            'pais_origem': 'País de Origem',
        }
