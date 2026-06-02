from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Livro


class BibliotecaAuthenticationForm(AuthenticationForm):
    """Username/password authentication form with Portuguese labels."""

    username = forms.CharField(
        label='Nome de utilizador',
        widget=forms.TextInput(attrs={
            'autofocus': True,
            'placeholder': 'utilizador01',
        }),
    )
    password = forms.CharField(
        label='Palavra-passe',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password',
            'placeholder': '********',
        }),
    )


class LivroForm(forms.ModelForm):
    """Form used by the create and update screens for Livro records."""

    class Meta:
        model = Livro
        fields = [
            'isbn',
            'titulo',
            'autor',
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
            'autor': 'Autores',
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
