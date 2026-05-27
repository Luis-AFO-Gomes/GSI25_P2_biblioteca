from django import forms

from .models import Livro


class LivroForm(forms.ModelForm):
    """Form used by the create and update screens for Livro records."""

    class Meta:
        model = Livro
        fields = [
            'isbn',
            'titulo',
            'idioma',
            'tipo',
            'tema',
            'editora',
            'data_pub',
            'original',
            'status',
        ]
        labels = {
            'isbn': 'ISBN',
            'titulo': 'Titulo',
            'idioma': 'Idioma',
            'tipo': 'Tipo',
            'tema': 'Tema',
            'editora': 'Editora',
            'data_pub': 'Data de publicacao',
            'original': 'Original',
            'status': 'Estado',
        }
        widgets = {
            'data_pub': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, readonly_isbn=False, **kwargs):
        super().__init__(*args, **kwargs)

        if readonly_isbn:
            self.fields['isbn'].disabled = True
            self.fields['isbn'].help_text = 'O ISBN nao pode ser alterado depois de criado.'
