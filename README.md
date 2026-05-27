# Biblioteca

Projecto Django para um catalogo simples de biblioteca publica. A aplicacao gere livros (`Livro`) e usa os dados de editoras (`Editora`) ja existentes na base de dados.

## Funcionalidades Actuais

- Listagem de livros na pagina inicial e na pagina de catalogo.
- Consulta de detalhes de um livro em modo apenas leitura.
- Insercao de novos livros.
- Edicao de livros existentes.
- Eliminacao permanente de livros, depois de uma pagina de confirmacao.
- Mensagens de confirmacao apos insercao, actualizacao e eliminacao.
- Pagina 404 com o layout normal do site para registos nao encontrados, quando o tratamento 404 personalizado esta activo.

## Limitacoes

- Nao existe interface para gerir `Editora`. As editoras devem ser geridas atraves do site de administracao Django ou de outra ferramenta de administracao SQLite.
- A eliminacao de livros e permanente nesta fase, apenas para demonstracao. Numa versao futura, o livro devera ser ocultado/desactivado sem remover o registo da base de dados.
- Os controlos de pesquisa e filtro no catalogo ainda sao apenas visuais.
- A base de dados SQLite e local ao projecto.
- O desenho das paginas e temporario e segue o aspecto visual ja existente ate existir um wireframe final.

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
                └── master.html
```

## Ficheiros Principais

- `biblioteca/manage.py`: ponto de entrada para comandos Django.
- `biblioteca/biblioteca/settings.py`: configuracao do projecto, apps instaladas, base de dados, ficheiros estaticos e middleware.
- `biblioteca/biblioteca/urls.py`: rotas principais do projecto, incluindo as rotas da app e o handler 404.
- `biblioteca/livros/models.py`: modelos de dados `Livro` e `Editora`.
- `biblioteca/livros/admin.py`: configuracao do site de administracao para livros e editoras.
- `biblioteca/livros/urls.py`: rotas da app para catalogo e CRUD de livros.
- `biblioteca/livros/views.py`: vistas baseadas em classes para listar, consultar, criar, editar, apagar e apresentar erros 404.
- `biblioteca/livros/templates/livros/master.html`: estrutura comum das paginas, com cabecalho, navegacao, mensagens, rodape e bloco de conteudo.
- `biblioteca/livros/templates/livros/_book_grid.html`: grelha reutilizavel de cartoes de livros.
- `biblioteca/livros/templates/livros/livro_form.html`: pagina partilhada para detalhe, insercao e edicao.
- `biblioteca/livros/templates/livros/livro_confirm_delete.html`: pagina de confirmacao de eliminacao.
- `biblioteca/livros/static/style/biblioteca.css`: estilos do site.

## Ficheiros Especiais

### `forms.py`

O ficheiro `forms.py` contem classes de formulario Django. Estas classes fazem a ligacao entre a interface de utilizador e os modelos de dados sem obrigar as views ou os templates a conhecerem todos os detalhes de validacao e apresentacao dos campos.

Neste projecto, `LivroForm` e baseado no modelo `Livro`, definido em `models.py`, mas e usado pelas views e templates para construir os campos HTML, aplicar validacoes basicas e controlar comportamentos de UI, como impedir a alteracao do ISBN durante a edicao.

Esta separacao ajuda a manter responsabilidades claras:

- `models.py` define estrutura e persistencia dos dados.
- `forms.py` define como esses dados sao recolhidos e validados na interface.
- `views.py` coordena o pedido HTTP, o formulario e a resposta.
- `templates` apresentam a interface visual ao utilizador.

### `services.py`

O ficheiro `services.py` contem classes e funcoes orientadas para logica de negocio ou acesso controlado aos dados. A ideia e evitar que as views fiquem carregadas com regras de procura, tratamento de erros ou operacoes de negocio.

Neste projecto, `LivroService` centraliza operacoes como listar livros, obter um livro por ISBN e apagar um livro. Internamente, continua a usar `models.py` para aceder a base de dados, mas oferece as views uma interface mais simples e preparada para crescer.

Esta organizacao facilita a evolucao da aplicacao:

- `models.py` continua focado na persistencia.
- `services.py` concentra regras e operacoes de negocio.
- `views.py` fica mais simples, tratando sobretudo de fluxo HTTP.
- `templates` ficam focados na experiencia visual e nao na logica de dados.

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
