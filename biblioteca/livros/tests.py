from django.contrib.auth.models import Group, User
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Autor, Editora, Livro, Tema, ZonasGeograficas


class LivroCrudTests(TestCase):
    def setUp(self):
        self.socio_group = Group.objects.create(name='socio')
        self.socio = User.objects.create_user(username='socio01', password='segredo-forte')
        self.socio.groups.add(self.socio_group)
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
        self.client.force_login(self.socio)

        response = self.client.get(reverse('livros:detalhe_livro', kwargs={'isbn': self.livro.isbn}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.livro.titulo)
        self.assertContains(response, self.livro.isbn)

    def test_create_book_persists_submitted_data(self):
        self.client.force_login(self.socio)

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
        self.client.force_login(self.socio)

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
        self.client.force_login(self.socio)

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
        self.client.force_login(self.socio)

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
        self.assertContains(response, 'membro')
        self.assertContains(response, 'Sair...')

    def test_header_shows_first_group_name_after_login(self):
        group = Group.objects.create(name='socio')
        self.user.groups.add(group)
        self.client.force_login(self.user)

        response = self.client.get(reverse('livros:lista_livros'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'socio')

    def test_logout_ends_session_and_redirects_to_catalogue(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('livros:logout'))

        self.assertRedirects(response, reverse('livros:lista_livros'))
        self.assertNotIn('_auth_user_id', self.client.session)


class PermissionTests(TestCase):
    def setUp(self):
        self.zona = ZonasGeograficas.objects.create(sigla='PT', nome='Portugal')
        self.autor = Autor.objects.create(
            id='A001',
            nome='Autor Teste',
            nacionalidade=self.zona,
        )
        self.tema = Tema.objects.create(sigla='DJG', nome='Django')
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
        self.membro_group = Group.objects.create(name='membro')
        self.socio_group = Group.objects.create(name='socio')
        self.administrador_group = Group.objects.create(name='administrador')

    def create_user_with_groups(self, username, groups):
        user = User.objects.create_user(username=username, password='segredo-forte')
        user.groups.set(groups)
        return user

    def test_public_catalog_shows_subscription_button_and_static_book_cards(self):
        response = self.client.get(reverse('livros:lista_livros'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Registo')
        self.assertContains(response, 'Sócio')
        self.assertContains(response, f'href="{reverse("livros:registo_socio")}"')
        self.assertNotContains(response, f'href="{reverse("livros:detalhe_livro", kwargs={"isbn": self.livro.isbn})}"')
        self.assertNotContains(response, 'Novo livro')
        self.assertNotContains(response, 'class="status"')

    def test_guest_detail_url_redirects_to_catalogue(self):
        response = self.client.get(reverse('livros:detalhe_livro', kwargs={'isbn': self.livro.isbn}))

        self.assertRedirects(response, reverse('livros:lista_livros'))

    def test_user_without_group_can_view_details_but_not_manage_books(self):
        user = User.objects.create_user(username='semgrupo', password='segredo-forte')
        self.client.force_login(user)

        detail = self.client.get(reverse('livros:detalhe_livro', kwargs={'isbn': self.livro.isbn}))
        create = self.client.get(reverse('livros:criar_livro'))
        edit = self.client.get(reverse('livros:editar_livro', kwargs={'isbn': self.livro.isbn}))
        delete = self.client.get(reverse('livros:apagar_livro', kwargs={'isbn': self.livro.isbn}))

        self.assertEqual(detail.status_code, 200)
        self.assertNotContains(detail, 'Editar')
        self.assertNotContains(detail, 'Apagar')
        self.assertRedirects(create, reverse('livros:lista_livros'))
        self.assertRedirects(edit, reverse('livros:detalhe_livro', kwargs={'isbn': self.livro.isbn}))
        self.assertRedirects(delete, reverse('livros:detalhe_livro', kwargs={'isbn': self.livro.isbn}))

    def test_membro_can_view_details_but_not_manage_books(self):
        membro = self.create_user_with_groups('membro01', [self.membro_group])
        self.client.force_login(membro)

        catalog = self.client.get(reverse('livros:lista_livros'))
        detail = self.client.get(reverse('livros:detalhe_livro', kwargs={'isbn': self.livro.isbn}))

        self.assertContains(catalog, f'href="{reverse("livros:detalhe_livro", kwargs={"isbn": self.livro.isbn})}"')
        self.assertContains(catalog, 'class="status"')
        self.assertNotContains(catalog, 'Novo livro')
        self.assertEqual(detail.status_code, 200)
        self.assertNotContains(detail, 'Editar')
        self.assertNotContains(detail, 'Apagar')

    def test_socio_can_manage_books(self):
        socio = self.create_user_with_groups('socio01', [self.socio_group])
        self.client.force_login(socio)

        catalog = self.client.get(reverse('livros:lista_livros'))
        detail = self.client.get(reverse('livros:detalhe_livro', kwargs={'isbn': self.livro.isbn}))
        create = self.client.get(reverse('livros:criar_livro'))

        self.assertContains(catalog, 'Novo livro')
        self.assertContains(detail, 'Editar')
        self.assertContains(detail, 'Apagar')
        self.assertEqual(create.status_code, 200)

    def test_administrador_can_manage_books(self):
        administrador = self.create_user_with_groups('admin01', [self.administrador_group])
        self.client.force_login(administrador)

        response = self.client.get(reverse('livros:criar_livro'))

        self.assertEqual(response.status_code, 200)

    def test_multiple_groups_use_highest_permission(self):
        user = self.create_user_with_groups('multi01', [self.membro_group, self.socio_group])
        self.client.force_login(user)

        response = self.client.get(reverse('livros:criar_livro'))

        self.assertEqual(response.status_code, 200)


class SubscriptionTests(TestCase):
    def test_subscription_page_uses_login_style_fields(self):
        response = self.client.get(reverse('livros:registo_socio'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Registo Sócio')
        self.assertContains(response, 'USERNAME')
        self.assertContains(response, 'Primeiro nome')
        self.assertContains(response, 'Confirmar palavra-passe')
        self.assertContains(response, 'auth-card')
        self.assertContains(response, 'auth-form')

    def test_valid_subscription_confirms_data_without_creating_user(self):
        response = self.client.post(
            reverse('livros:registo_socio'),
            {
                'username': 'novo_socio',
                'first_name': 'Novo',
                'last_name': 'Socio',
                'email': 'novo@example.com',
                'password': 'Senha-Forte-2026',
                'confirm_password': 'Senha-Forte-2026',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='novo_socio').exists())
        self.assertContains(response, 'Funcionalidade não implementada, o utilizador NÃO FOI ADICIONADO')
        self.assertContains(response, 'novo_socio')
        self.assertContains(response, 'Novo')
        self.assertContains(response, 'Socio')
        self.assertContains(response, 'novo@example.com')
        self.assertNotContains(response, 'Senha-Forte-2026')

    def test_subscription_rejects_existing_username(self):
        User.objects.create_user(username='existente', password='segredo-forte')

        response = self.client.post(
            reverse('livros:registo_socio'),
            {
                'username': 'existente',
                'first_name': 'Nome',
                'last_name': 'Apelido',
                'email': 'existente@example.com',
                'password': 'Senha-Forte-2026',
                'confirm_password': 'Senha-Forte-2026',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Este nome de utilizador ja existe.')

    def test_subscription_rejects_password_mismatch(self):
        response = self.client.post(
            reverse('livros:registo_socio'),
            {
                'username': 'novo_socio',
                'first_name': 'Novo',
                'last_name': 'Socio',
                'email': 'novo@example.com',
                'password': 'Senha-Forte-2026',
                'confirm_password': 'Senha-Diferente-2026',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'As palavras-passe nao coincidem.')
        self.assertFalse(User.objects.filter(username='novo_socio').exists())

    def test_subscription_uses_django_password_validators(self):
        response = self.client.post(
            reverse('livros:registo_socio'),
            {
                'username': 'novo_socio',
                'first_name': 'Novo',
                'last_name': 'Socio',
                'email': 'novo@example.com',
                'password': '123',
                'confirm_password': '123',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This password is too short.')
        self.assertFalse(User.objects.filter(username='novo_socio').exists())
