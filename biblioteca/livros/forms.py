from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

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


class SubscriptionForm(forms.Form):
    """Public subscription request form. It validates only; it does not create users."""

    username = forms.CharField(
        label='USERNAME',
        max_length=150,
        widget=forms.TextInput(attrs={
            'autofocus': True,
            'placeholder': 'utilizador01',
        }),
    )
    first_name = forms.CharField(
        label='Primeiro nome',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Nome'}),
    )
    last_name = forms.CharField(
        label='Apelido',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Apelido'}),
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'utilizador@example.com'}),
    )
    password = forms.CharField(
        label='Palavra-passe',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    confirm_password = forms.CharField(
        label='Confirmar palavra-passe',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError('Este nome de utilizador ja existe.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        username = cleaned_data.get('username')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'As palavras-passe nao coincidem.')

        if password:
            user = User(
                username=username or '',
                first_name=cleaned_data.get('first_name', ''),
                last_name=cleaned_data.get('last_name', ''),
                email=cleaned_data.get('email', ''),
            )
            try:
                validate_password(password, user=user)
            except ValidationError as error:
                self.add_error('password', error)

        return cleaned_data


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
