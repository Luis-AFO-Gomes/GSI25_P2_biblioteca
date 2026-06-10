# Biblioteca - Permissões

Projecto Django para um catálogo simples de biblioteca pública. Esta etapa (`stg09_permissions`) adiciona regras de acesso por perfil, mantém o catálogo público e introduz uma página pública de pedido de registo de sócio sem criar utilizadores na base de dados.

## Funcionalidades Actuais

- Página inicial pública.
- Catálogo público com listagem de livros.
- Visitantes não autenticados vêem os livros no catálogo, mas os cartões não são clicáveis.
- Visitantes não autenticados não vêem a disponibilidade/estado dos livros.
- Acesso directo de visitantes a detalhes de livro redirecciona para o catálogo, sem mensagem adicional.
- Botão `Registo Sócio` no catálogo para visitantes não autenticados.
- Página pública de registo de sócio com o mesmo estilo visual da página de login.
- Formulário de registo de sócio com campos `USERNAME`, primeiro nome, apelido, email, palavra-passe e confirmação de palavra-passe.
- Validação de `USERNAME` único na tabela de utilizadores.
- Validação de confirmação de palavra-passe.
- Validação de palavra-passe através dos validadores nativos do Django.
- O pedido de registo de sócio valida e mostra os dados inseridos, mas não cria utilizador na base de dados.
- Mensagem de confirmação do registo: `Funcionalidade não implementada, o utilizador NÃO FOI ADICIONADO`.
- Login com nome de utilizador e palavra-passe usando o sistema nativo `django.contrib.auth`.
- Logout através do menu de utilizador no cabeçalho.
- Menu do utilizador com o primeiro grupo associado ao utilizador ou `membro` quando não existe grupo atribuído.
- Utilizadores autenticados vêem detalhes de livros e a disponibilidade/estado dos livros.
- Utilizadores do grupo `membro`, ou sem grupo, não podem criar, editar ou apagar livros.
- Utilizadores dos grupos `socio` e `administrador` podem criar, consultar, editar e apagar livros.
- Quando um utilizador tem vários grupos, vence a permissão mais elevada.
- A gestão de utilizadores e grupos continua a ser feita através do site de administração Django.

## Perfis E Grupos

- `guest`: perfil implícito para visitantes não autenticados. Pode ver a página inicial, o catálogo e a página de registo de sócio.
- `membro`: grupo para utilizadores autenticados com acesso a detalhes dos livros, sem permissões de criação, edição ou eliminação.
- `socio`: grupo para utilizadores autenticados com permissões completas de CRUD sobre livros.
- `administrador`: grupo para utilizadores autenticados com as mesmas permissões de `socio` nesta etapa.

Utilizadores autenticados sem grupo são tratados como `membro`. A aplicação ainda não impede múltiplos grupos por utilizador; quando isso acontece, é aplicada a permissão mais elevada.

## Limitações

- O registo de sócio ainda não cria utilizadores nem guarda pedidos pendentes.
- A validação administrativa de novos sócios será implementada numa etapa futura.
- `socio` e `administrador` têm o mesmo comportamento nesta etapa.
- O login aceita apenas nome de utilizador e palavra-passe.
- A base de dados SQLite é local ao projecto.

## Estrutura De Pastas

```text
GSI25_P2_biblioteca/
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── pyProject.toml
├── image.png
└── biblioteca/
    ├── manage.py
    ├── db.sqlite3
    ├── biblioteca/
    │   ├── settings.py
    │   ├── urls.py
    │   ├── asgi.py
    │   ├── wsgi.py
    │   └── __init__.py
    └── livros/
        ├── admin.py
        ├── apps.py
        ├── forms.py
        ├── models.py
        ├── services.py
        ├── tests.py
        ├── urls.py
        ├── views.py
        ├── migrations/
        │   ├── 0001_initial.py
        │   ├── 0002_editora_alter_livro_editora.py
        │   ├── 0003_tema.py
        │   ├── 0004_rename_livros_livr_tema_228879_idx_livros_livr_tema_id_504149_idx_and_more.py
        │   ├── 0005_autor_alter_livro_data_pub_livro_autor_and_more.py
        │   └── __init__.py
        ├── static/
        │   └── style/
        │       └── biblioteca.css
        └── templates/
            └── livros/
                ├── 404.html
                ├── _book_grid.html
                ├── home.html
                ├── livro_confirm_delete.html
                ├── livro_form.html
                ├── livros.html
                ├── login.html
                ├── master.html
                └── subscription.html
```

## Documentação Detalhada

- [Authentication workflow](docs/authentication-workflow.md): explicação passo a passo do fluxo Python/Django de autenticação, autorização por grupos, templates envolvidos e testes relacionados.

## Ficheiros Principais

- `biblioteca/manage.py`: ponto de entrada para comandos Django.
- `biblioteca/biblioteca/settings.py`: configuração do projecto, incluindo URLs de login, redireccionamento de login e redireccionamento de logout.
- `biblioteca/biblioteca/urls.py`: rotas principais do projecto, incluindo as rotas da app, o site de administração e o handler 404.
- `biblioteca/livros/forms.py`: formulários Django para autenticação, livros e pedido de registo de sócio.
- `biblioteca/livros/urls.py`: rotas da app para catálogo, autenticação, registo de sócio e CRUD de livros.
- `biblioteca/livros/views.py`: vistas de autenticação, registo de sócio, catálogo, detalhes e CRUD com regras de permissões.
- `biblioteca/livros/templates/livros/master.html`: estrutura comum das páginas, cabeçalho, navegação, menu de utilizador, mensagens e rodapé.
- `biblioteca/livros/templates/livros/login.html`: página de login de utilizador.
- `biblioteca/livros/templates/livros/subscription.html`: página pública de registo de sócio.
- `biblioteca/livros/templates/livros/_book_grid.html`: grelha de livros com comportamento diferente para público e utilizadores autenticados.
- `biblioteca/livros/static/style/biblioteca.css`: estilos do site, incluindo login, registo, menu de utilizador e cartões de livros.
- `biblioteca/livros/tests.py`: testes para autenticação, permissões, registo de sócio, CRUD de livros e página 404.

## Ficheiros Especiais

### `forms.py`

`BibliotecaAuthenticationForm` mantém o login nativo do Django com rótulos em português.

`SubscriptionForm` valida pedidos públicos de registo de sócio. O formulário verifica se o `USERNAME` já existe, confirma se as palavras-passe coincidem e usa `validate_password` para aplicar os validadores nativos do Django. Mesmo quando o formulário é válido, nenhum utilizador é criado.

`LivroForm` continua baseado no modelo `Livro` e é usado nas páginas de criação e edição de livros. Na edição, o ISBN permanece bloqueado para impedir alteração da chave do registo.

### `views.py`

`can_view_book_detail` e `can_manage_books` concentram as regras de acesso desta etapa. Visitantes não autenticados só podem consultar a listagem pública. Utilizadores autenticados podem consultar detalhes. Apenas `socio` e `administrador` podem criar, editar e apagar livros.

`SubscriptionView` apresenta e valida o formulário de registo de sócio, confirma os dados inseridos e mostra explicitamente que a funcionalidade ainda não cria utilizadores.

### `templates`

`livros.html` mostra `Registo Sócio` para visitantes, `Novo livro` para utilizadores com permissão de gestão e nenhum botão de criação para `membro`.

`_book_grid.html` remove links e disponibilidade para visitantes, mantendo detalhes e estado visíveis para utilizadores autenticados.

`livro_form.html` só apresenta `Editar` e `Apagar` a utilizadores com permissão de gestão.

## Change Log - Ficheiros Principais

- `biblioteca/livros/forms.py`: adicionada `SubscriptionForm` com validação de `USERNAME` único, confirmação de palavra-passe e validadores nativos do Django.
- `biblioteca/livros/urls.py`: adicionada a rota `registo-socio/`.
- `biblioteca/livros/views.py`: adicionadas regras de autorização por grupos `membro`, `socio` e `administrador`; adicionada `SubscriptionView`; protegidos detalhes e CRUD por redireccionamento.
- `biblioteca/livros/templates/livros/livros.html`: botão de acção passa a depender do perfil do utilizador.
- `biblioteca/livros/templates/livros/_book_grid.html`: cartões deixam de ser clicáveis para visitantes e escondem disponibilidade no catálogo público.
- `biblioteca/livros/templates/livros/livro_form.html`: botões `Editar` e `Apagar` ficam disponíveis apenas para `socio` e `administrador`.
- `biblioteca/livros/templates/livros/master.html`: perfil sem grupo passa a aparecer como `membro`; nome do utilizador usa `username` quando não existe nome completo.
- `biblioteca/livros/templates/livros/subscription.html`: nova página pública de registo de sócio.
- `biblioteca/livros/static/style/biblioteca.css`: adicionados estilos para cartões não clicáveis e resumo do registo.
- `biblioteca/livros/tests.py`: adicionados testes para permissões por grupo, registo de sócio e visibilidade pública/autenticada.
- `README.md`: actualizado para documentar a etapa `stg09_permissions`.

## Instalação

Criar e activar um ambiente virtual a partir da raiz do repositório:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instalar dependências de execução:

```powershell
python -m pip install -r requirements.txt
```

Para dependências de desenvolvimento:

```powershell
python -m pip install -r requirements-dev.txt
```

## Base De Dados

O projecto usa SQLite:

```text
biblioteca/db.sqlite3
```

Aplicar migrações quando necessário:

```powershell
cd biblioteca
python manage.py migrate
```

Criar utilizador de administração, se necessário:

```powershell
python manage.py createsuperuser
```

Site de administração:

```text
http://127.0.0.1:8000/admin/
```

Os utilizadores e grupos `membro`, `socio` e `administrador` devem ser criados e mantidos no site de administração Django.

## Executar

A partir da pasta interior `biblioteca`:

```powershell
python manage.py runserver
```

Abrir:

```text
http://127.0.0.1:8000/
```

Páginas úteis:

- Início: `http://127.0.0.1:8000/`
- Catálogo: `http://127.0.0.1:8000/catalogo/`
- Login: `http://127.0.0.1:8000/login/`
- Registo de sócio: `http://127.0.0.1:8000/registo-socio/`
- Novo livro: `http://127.0.0.1:8000/livro/novo/`
- Administração: `http://127.0.0.1:8000/admin/`

As mesmas rotas da app também estão disponíveis com o prefixo `/livros/`, porque a configuração principal inclui a app na raiz e em `/livros/`.

## Testar E Validar

Executar verificações do Django:

```powershell
cd biblioteca
python manage.py check
```

Executar testes:

```powershell
python manage.py test
```
