# Biblioteca - Autenticacao

Projecto Django para um catalogo simples de biblioteca publica. Esta etapa adiciona autenticacao nativa do Django com utilizadores e grupos geridos atraves do site de administracao.

## Funcionalidades Actuais

- Login com nome de utilizador e palavra-passe usando o sistema nativo `django.contrib.auth`.
- Logout atraves do menu de utilizador no cabecalho.
- Redireccionamento de utilizadores autenticados para a pagina de catalogo apos login.
- Redireccionamento para a pagina de catalogo apos logout.
- Botao `Login` no cabecalho para visitantes nao autenticados.
- Botao com o nome do utilizador no cabecalho apos autenticacao.
- Menu do utilizador com o primeiro grupo associado ao utilizador ou `member` quando nao existe grupo atribuido.
- Gestao de utilizadores e grupos atraves do site de administracao Django.
- Permissoes iguais para todos os utilizadores nesta etapa; a diferenciacao por perfil/grupo sera implementada em etapas futuras.

## Perfis E Grupos Planeados

- `Administrators`: grupo previsto para administradores da biblioteca.
- `Partners`: grupo previsto para parceiros da biblioteca.
- `Members`: grupo previsto para membros autenticados.
- `Guest`: perfil implicito para visitantes sem autenticacao.

Nesta etapa, a aplicacao apenas apresenta o primeiro grupo do utilizador no menu. A regra de garantir uma unica associacao de grupo por utilizador ainda nao esta implementada.

## Limitacoes

- O login aceita apenas nome de utilizador e palavra-passe; autenticacao por email ou provedores externos como Google e Microsoft fica para etapas futuras.
- Nao existe ainda controlo de permissoes por grupo nas paginas ou nos botoes de accao.
- Utilizadores sem grupo aparecem com o perfil `member` no cabecalho, mas essa classificacao ainda nao altera o acesso.
- A pagina de catalogo continua publica para visitantes sem autenticacao.
- A criacao, edicao e eliminacao de livros ainda nao foram protegidas por permissoes nesta etapa.
- A base de dados SQLite e local ao projecto.

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
    |   ├── settings.py
    |   ├── urls.py
    |   ├── asgi.py
    |   ├── wsgi.py
    |   └── __init__.py
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
        |   ├── 0001_initial.py
        |   ├── 0002_editora_alter_livro_editora.py
        |   └── __init__.py
        ├── static/
        |   └── style/
        |       └── biblioteca.css
        └── templates/
            └── livros/
                ├── 404.html
                ├── _book_grid.html
                ├── home.html
                ├── livro_confirm_delete.html
                ├── livro_form.html
                ├── livros.html
                ├── login.html
                └── master.html
```

## Ficheiros Principais

- `biblioteca/manage.py`: ponto de entrada para comandos Django.
- `biblioteca/biblioteca/settings.py`: configuracao do projecto, incluindo URLs de login, redireccionamento de login e redireccionamento de logout.
- `biblioteca/biblioteca/urls.py`: rotas principais do projecto, incluindo as rotas da app, o site de administracao e o handler 404.
- `biblioteca/livros/forms.py`: formularios Django, incluindo o formulario de autenticacao com rotulos em portugues.
- `biblioteca/livros/urls.py`: rotas da app para catalogo, autenticacao e CRUD de livros.
- `biblioteca/livros/views.py`: vistas para login, logout, listar, consultar, criar, editar, apagar e apresentar erros 404.
- `biblioteca/livros/templates/livros/master.html`: estrutura comum das paginas, com cabecalho, navegacao, menu de autenticacao, mensagens, rodape e bloco de conteudo.
- `biblioteca/livros/templates/livros/login.html`: pagina de login de utilizador.
- `biblioteca/livros/static/style/biblioteca.css`: estilos do site, incluindo cabecalho autenticado, menu de utilizador e pagina de login.
- `biblioteca/livros/tests.py`: testes para CRUD de livros, pagina 404 e fluxo de autenticacao.

## Ficheiros Especiais

### `forms.py`

O ficheiro `forms.py` contem classes de formulario Django. Estas classes fazem a ligacao entre a interface de utilizador e os modelos ou servicos de autenticacao sem obrigar as views ou os templates a conhecerem todos os detalhes de validacao e apresentacao dos campos.

Nesta etapa, `BibliotecaAuthenticationForm` estende o formulario nativo de autenticacao do Django para manter o login por nome de utilizador e palavra-passe com textos em portugues. O formulario continua a usar a validacao nativa de credenciais do Django.

`LivroForm` continua baseado no modelo `Livro`, definido em `models.py`, e e usado pelas views e templates para construir os campos HTML, aplicar validacoes basicas e controlar comportamentos de UI, como impedir a alteracao do ISBN durante a edicao.

Esta separacao ajuda a manter responsabilidades claras:

- `models.py` define estrutura e persistencia dos dados.
- `forms.py` define como dados e credenciais sao recolhidos e validados na interface.
- `views.py` coordena o pedido HTTP, os formularios e a resposta.
- `templates` apresentam a interface visual ao utilizador.

### `views.py`

O ficheiro `views.py` contem as vistas da aplicacao. Para autenticacao, `BibliotecaLoginView` e `BibliotecaLogoutView` reutilizam as vistas nativas do Django, mantendo o comportamento padrao de sessao e seguranca.

O login bem sucedido encaminha o utilizador para o catalogo. O logout termina a sessao e tambem encaminha para o catalogo. As restantes vistas continuam a tratar o fluxo HTTP das paginas de livros.

### `services.py`

O ficheiro `services.py` contem classes e funcoes orientadas para logica de negocio ou acesso controlado aos dados. A ideia e evitar que as views fiquem carregadas com regras de procura, tratamento de erros ou operacoes de negocio.

Neste projecto, `LivroService` centraliza operacoes como listar livros, obter um livro por ISBN e apagar um livro. Internamente, continua a usar `models.py` para aceder a base de dados, mas oferece as views uma interface mais simples e preparada para crescer.

Esta organizacao facilita a evolucao da aplicacao:

- `models.py` continua focado na persistencia.
- `services.py` concentra regras e operacoes de negocio.
- `views.py` fica mais simples, tratando sobretudo de fluxo HTTP e autenticacao.
- `templates` ficam focados na experiencia visual e nao na logica de dados.

## Principais Alteracoes Nos Ficheiros Principais

- `biblioteca/biblioteca/settings.py`: adicionadas as configuracoes `LOGIN_URL`, `LOGIN_REDIRECT_URL` e `LOGOUT_REDIRECT_URL` para centralizar os destinos de login, pos-login e logout.
- `biblioteca/livros/forms.py`: adicionada a classe `BibliotecaAuthenticationForm`, baseada em `AuthenticationForm`, para manter o login nativo do Django com rotulos e placeholders em portugues.
- `biblioteca/livros/urls.py`: adicionadas as rotas `login/` e `logout/` para expor o fluxo de autenticacao dentro da app `livros`.
- `biblioteca/livros/views.py`: adicionadas as classes `BibliotecaLoginView` e `BibliotecaLogoutView`, reutilizando as views nativas do Django para autenticar por nome de utilizador/palavra-passe, terminar sessao e redireccionar para o catalogo.
- `README.md`: actualizado para documentar a etapa de autenticacao, os grupos planeados, as limitacoes actuais e as rotas uteis de login e administracao.

## Instalacao

Criar e activar um ambiente virtual a partir da raiz do repositorio:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instalar dependencias de execucao:

```powershell
python -m pip install -r requirements.txt
```

Para dependencias de desenvolvimento:

```powershell
python -m pip install -r requirements-dev.txt
```

## Base De Dados

O projecto usa SQLite:

```text
biblioteca/db.sqlite3
```

Aplicar migracoes quando necessario:

```powershell
cd biblioteca
python manage.py migrate
```

Criar utilizador de administracao, se necessario:

```powershell
python manage.py createsuperuser
```

Site de administracao:

```text
http://127.0.0.1:8000/admin/
```

Os utilizadores e grupos devem ser criados e mantidos no site de administracao Django.

## Executar

A partir da pasta interior `biblioteca`:

```powershell
python manage.py runserver
```

Abrir:

```text
http://127.0.0.1:8000/
```

Paginas uteis:

- Inicio: `http://127.0.0.1:8000/`
- Catalogo: `http://127.0.0.1:8000/catalogo/`
- Login: `http://127.0.0.1:8000/login/`
- Novo livro: `http://127.0.0.1:8000/livro/novo/`
- Administracao: `http://127.0.0.1:8000/admin/`

As mesmas rotas da app tambem estao disponiveis com o prefixo `/livros/`, porque a configuracao principal inclui a app na raiz e em `/livros/`.

## Testar E Validar

Executar verificacoes do Django:

```powershell
cd biblioteca
python manage.py check
```

Executar testes:

```powershell
python manage.py test
```
