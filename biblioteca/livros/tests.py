from django.contrib.auth.models import Group, User
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Autor, Editora, Livro, Tema, ZonasGeograficas


class LivroCrudTests(TestCase):
    def setUp(self):
        self.zona = ZonasGeograficas.objects.create(sigla='PT', nome='Portugal')
        self.autor = Autor.objects.create(
            id='A001',
            nome='Autor Teste',
            nacionalidade=self.zona,
        )
        self.tema = Tema.objects.create(sigla='DJG', nome='Django')
        self.outro_tema = Tema.objects.create(sigla='PY', nome='Python')
        self.editora = Editora.objects.create(
            nipc='123456789',
            nome='Editora Teste',
            contacto='teste@example.com',
            morada='Rua de Teste',
        )
        self.livro = Livro.objects.create(
            isbn='9781234567890',
            titulo='Livro Existente',
            idioma='PT',
            tipo='Manual',
            tema=self.tema,
            editora=self.editora,
            data_pub='2026-01-10',
            original=True,
            status=Livro.Status.DISPONIVEL,
        )
        self.livro.autor.set([self.autor])

    def test_detail_page_uses_existing_book_data(self):
        response = self.client.get(reverse('livros:detalhe_livro', kwargs={'isbn': self.livro.isbn}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.livro.titulo)
        self.assertContains(response, self.livro.isbn)

    def test_create_book_persists_submitted_data(self):
        response = self.client.post(
            reverse('livros:criar_livro'),
            {
                'isbn': '9789876543210',
                'titulo': 'Livro Novo',
                'idioma': 'PT',
                'tipo': 'Romance',
                'autor': [self.autor.id],
                'tema': self.tema.sigla,
                'editora': self.editora.nipc,
                'data_pub': '2026-02-15',
                'original': 'on',
                'status': Livro.Status.SUGERIDO,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Livro.objects.filter(isbn='9789876543210', titulo='Livro Novo').exists())
        self.assertContains(response, 'Livro inserido com sucesso.')

    def test_update_book_keeps_original_isbn(self):
        response = self.client.post(
            reverse('livros:editar_livro', kwargs={'isbn': self.livro.isbn}),
            {
                'isbn': '9780000000000',
                'titulo': 'Titulo Atualizado',
                'idioma': 'PT',
                'tipo': 'Manual',
                'autor': [self.autor.id],
                'tema': self.outro_tema.sigla,
                'editora': self.editora.nipc,
                'data_pub': '2026-01-10',
                'original': 'on',
                'status': Livro.Status.RESERVADO,
            },
            follow=True,
        )

        self.livro.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.livro.isbn, '9781234567890')
        self.assertEqual(self.livro.titulo, 'Titulo Atualizado')
        self.assertContains(response, 'Livro atualizado com sucesso.')

    def test_delete_book_requires_post_confirmation(self):
        confirmation = self.client.get(reverse('livros:apagar_livro', kwargs={'isbn': self.livro.isbn}))
        self.assertEqual(confirmation.status_code, 200)
        self.assertTrue(Livro.objects.filter(isbn=self.livro.isbn).exists())

        response = self.client.post(
            reverse('livros:apagar_livro', kwargs={'isbn': self.livro.isbn}),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Livro.objects.filter(isbn=self.livro.isbn).exists())
        self.assertContains(response, 'apagado com sucesso.')

    @override_settings(DEBUG=False, ALLOWED_HOSTS=['testserver'])
    def test_missing_book_uses_site_404_page(self):
        response = self.client.get(reverse('livros:detalhe_livro', kwargs={'isbn': '0000000000000'}))

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, 'Livro nao encontrado.', status_code=404)
        self.assertContains(response, 'Biblioteca Publica', status_code=404)


class AuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='leitor01', password='segredo-forte')

    def test_login_page_uses_portuguese_username_password_form(self):
        response = self.client.get(reverse('livros:login'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login de utilizador')
        self.assertContains(response, 'Nome de utilizador')
        self.assertContains(response, 'Palavra-passe')
        self.assertContains(response, 'Voltar ao catalogo')

    def test_login_authenticates_user_and_redirects_to_catalogue(self):
        response = self.client.post(
            reverse('livros:login'),
            {'username': 'leitor01', 'password': 'segredo-forte'},
        )

        self.assertRedirects(response, reverse('livros:lista_livros'))

    def test_header_shows_login_button_for_anonymous_user(self):
        response = self.client.get(reverse('livros:lista_livros'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'href="{reverse("livros:login")}"')
        self.assertContains(response, 'Login')

    def test_header_shows_username_and_default_member_profile_after_login(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('livros:lista_livros'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'leitor01')
        self.assertContains(response, 'member')
        self.assertContains(response, 'Sair...')

    def test_header_shows_first_group_name_after_login(self):
        group = Group.objects.create(name='Partners')
        self.user.groups.add(group)
        self.client.force_login(self.user)

        response = self.client.get(reverse('livros:lista_livros'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Partners')

    def test_logout_ends_session_and_redirects_to_catalogue(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('livros:logout'))

        self.assertRedirects(response, reverse('livros:lista_livros'))
        self.assertNotIn('_auth_user_id', self.client.session)
