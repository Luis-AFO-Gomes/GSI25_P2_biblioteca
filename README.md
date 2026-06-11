# Biblioteca - Envio De Email

Projecto Django para um catálogo simples de biblioteca pública. Esta etapa (`stg10_mailSender`) adiciona um exemplo simples de envio de email de confirmação quando o pedido público de registo de sócio é validado.

O envio real ainda não está activo: a configuração padrão usa o backend de consola do Django para mostrar a mensagem no terminal.

## Funcionalidades Actuais

- Página pública de registo de sócio em `registo-socio/`.
- Formulário de registo com `USERNAME`, primeiro nome, apelido, email, palavra-passe e confirmação.
- Validação de `USERNAME` único na tabela de utilizadores.
- Validação de confirmação de palavra-passe.
- Validação de palavra-passe através dos validadores nativos do Django.
- O pedido de registo valida os dados e mostra a página de confirmação, mas não cria utilizador na base de dados.
- Quando a página de confirmação é mostrada, é enviado um email HTML para o email indicado pelo novo sócio.
- O email contém a mensagem `O seu pedido de registo de sócio foi criado e aguarda validação por gestor da biblioteca`.
- O email contém uma tabela com os dados inseridos, sem incluir palavra-passe.
- As configurações de email são lidas a partir do ficheiro `.env`.
- A conta remetente de demonstração é `biblioteca@gmail.com`.
- O backend actual é `django.core.mail.backends.console.EmailBackend`, por isso nenhum email real é enviado.

## Limitações

- O registo de sócio ainda não cria utilizadores nem guarda pedidos pendentes.
- A validação administrativa de novos sócios será implementada numa etapa futura.
- O email é apenas demonstrativo enquanto for usado o backend de consola.
- Para envio real por Gmail será necessário trocar o backend e configurar uma app password válida.

## Estrutura De Pastas

```text
GSI25_P2_biblioteca/
|-- .env                  # ficheiro local ignorado pelo git
|-- .env.example          # exemplo de configuração de ambiente
|-- README.md
|-- requirements.txt
|-- requirements-dev.txt
|-- pyProject.toml
|-- image.png
`-- biblioteca/
    |-- manage.py
    |-- db.sqlite3
    |-- biblioteca/
    |   |-- settings.py
    |   |-- urls.py
    |   |-- asgi.py
    |   |-- wsgi.py
    |   `-- __init__.py
    `-- livros/
        |-- admin.py
        |-- apps.py
        |-- forms.py
        |-- mail.py
        |-- models.py
        |-- services.py
        |-- tests.py
        |-- urls.py
        |-- views.py
        |-- migrations/
        |-- static/
        |   `-- style/
        |       `-- biblioteca.css
        `-- templates/
            `-- livros/
                |-- emails/
                |   `-- subscription_confirmation.html
                |-- 404.html
                |-- _book_grid.html
                |-- home.html
                |-- livro_confirm_delete.html
                |-- livro_form.html
                |-- livros.html
                |-- login.html
                |-- master.html
                `-- subscription.html
```

## Ficheiros Principais

- `biblioteca/biblioteca/settings.py`: carrega `.env` com `python-dotenv` e define a configuração de email.
- `biblioteca/livros/mail.py`: constrói e envia o email HTML de confirmação do pedido de registo.
- `biblioteca/livros/views.py`: chama o envio de email quando o formulário de registo é válido e a confirmação é apresentada.
- `biblioteca/livros/templates/livros/emails/subscription_confirmation.html`: template HTML do email, com mensagem e tabela de dados.
- `.env.example`: exemplo de variáveis de ambiente para backend de consola e Gmail.
- `.env`: configuração local usada em desenvolvimento, ignorada pelo git.
- `biblioteca/livros/tests.py`: testes do registo e da mensagem HTML sem envio real.

## Change Log - Ficheiros Principais

- `.env.example`: adicionado exemplo de configuração de ambiente e email.
- `.env`: adicionado ficheiro local de desenvolvimento com backend de consola.
- `biblioteca/biblioteca/settings.py`: adicionada leitura de variáveis de ambiente e configuração de email.
- `biblioteca/livros/mail.py`: adicionado helper de envio de confirmação de registo de sócio.
- `biblioteca/livros/views.py`: envio do email após validação do pedido de registo.
- `biblioteca/livros/templates/livros/emails/subscription_confirmation.html`: adicionado template HTML do email.
- `biblioteca/livros/tests.py`: actualizado teste de registo para validar destinatário, remetente, HTML e ausência de palavra-passe.
- `README.md`: substituído por documentação específica da etapa `stg10_mailSender`.

## Documentação Adicional

- [Fluxos CRUD Django (ORM com SQLite)](docs/crud-workflows.md): explicacao detalhada dos fluxos de listagem, detalhe, insercao, edicao e eliminacao, incluindo onde acontecem os equivalentes de `SELECT`, `INSERT`, `UPDATE` e `DELETE`.
- [Fluxo de Autenticação com Django](docs/authentication-workflow.md): explicação passo a passo do fluxo Python/Django de autenticação, autorização por grupos, templates envolvidos e testes relacionados.


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

## Configuração De Email

O ficheiro `.env` fica na raiz do repositório e é carregado por `biblioteca/biblioteca/settings.py`.

Configuração usada nesta etapa, sem envio real:

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=biblioteca@gmail.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=biblioteca@gmail.com
EMAIL_HOST_PASSWORD=
```

Para testar envio real com Gmail numa etapa futura, trocar o backend e usar uma app password:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
DEFAULT_FROM_EMAIL=biblioteca@gmail.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=biblioteca@gmail.com
EMAIL_HOST_PASSWORD=app-password-do-gmail
```

Notas para Gmail:

- A conta deve ter autenticação de dois factores activa.
- A password usada deve ser uma app password, não a password normal da conta.
- Nesta etapa estes dados são apenas exemplos de demonstração.

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
- Administração: `http://127.0.0.1:8000/admin/`

Ao submeter um pedido válido em `registo-socio/`, o email HTML é escrito na consola onde o servidor Django está a correr.

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
