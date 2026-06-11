# Fluxo de autenticação

Este documento explica como a autenticação e a autorização funcionam neste projecto Django, e em que ficheiros acontece cada etapa.

## 1. O Django está configurado como fornecedor de autenticação

O projecto usa o sistema nativo de autenticação do Django em vez de um modelo de utilizador personalizado.

- `biblioteca/biblioteca/settings.py` inclui `django.contrib.auth`, que fornece os modelos `User`, `Group`, permissões, hashing de palavras-passe e os backends de autenticação usados pelo Django.
- O mesmo ficheiro inclui `django.contrib.sessions`, que guarda a sessão do utilizador autenticado, e `django.contrib.messages`, usado para mensagens de sucesso após operações CRUD de livros.
- `SessionMiddleware` tem de executar antes de `AuthenticationMiddleware`, porque a autenticação lê o id do utilizador a partir da sessão. Neste projecto, a ordem está correta: o middleware de sessão aparece antes do middleware de autenticação.
- `AuthenticationMiddleware` adiciona `request.user` a todos os pedidos. Esse é o objecto usado nas views e templates para saber se o visitante é anónimo, autenticado ou pertence a um grupo.
- Os context processors incluem `django.template.context_processors.request` e `django.contrib.auth.context_processors.auth`, o que torna `request` e dados relacionados com autenticação disponíveis nos templates.
- `LOGIN_URL`, `LOGIN_REDIRECT_URL` e `LOGOUT_REDIRECT_URL` definem as URLs padrão de autenticação e redirecionamento usadas pelas views de autenticação do Django.

Ficheiro relevante: `biblioteca/biblioteca/settings.py`.

## 2. O routing envia pedidos de login/logout para as views da app

A configuração principal de URLs inclui `livros.urls` na raiz do site. Por isso, `/login/`, `/logout/`, `/catalogo/` e as rotas dos livros são resolvidas pela app `livros`.

A configuração de URLs da app faz o mapeamento seguinte:

- `/login/` para `BibliotecaLoginView`.
- `/logout/` para `BibliotecaLogoutView`.
- `/registo-socio/` para `SubscriptionView`.
- `/catalogo/` para `ListaLivrosView`.
- `/livro/novo/`, `/livro/<isbn>/editar/` e `/livro/<isbn>/apagar/` para as views protegidas de gestão de livros.
- `/livro/<isbn>/` para a view protegida de detalhes do livro.

Ficheiros relevantes:

- `biblioteca/biblioteca/urls.py`
- `biblioteca/livros/urls.py`

## 3. O formulário de login usa o AuthenticationForm nativo do Django

`BibliotecaAuthenticationForm` é uma pequena personalização do `AuthenticationForm` do Django.

Ele não implementa uma verificação própria da palavra-passe. Em vez disso, herda o fluxo normal de validação de username/password do Django e altera apenas labels/placeholders para português:

1. O browser envia `username`, `password` e o token CSRF para `/login/`.
2. `BibliotecaLoginView`, por herdar de `LoginView`, instancia `BibliotecaAuthenticationForm`.
3. O `AuthenticationForm` herdado do Django valida as credenciais usando os mecanismos internos de autenticação do Django.
4. Se as credenciais forem inválidas, os erros gerais do formulário são devolvidos ao template de login.
5. Se as credenciais forem válidas, a `LoginView` do Django autentica o utilizador escrevendo os dados de autenticação na sessão.

Ficheiros relevantes:

- `biblioteca/livros/forms.py`
- `biblioteca/livros/views.py`
- `biblioteca/livros/templates/livros/login.html`

## 4. A view de login delega quase todo o trabalho na LoginView do Django

`BibliotecaLoginView` herda de `django.contrib.auth.views.LoginView`.

A configuração específica do projecto é:

- `template_name = 'livros/login.html'`: usa o template de login deste projecto.
- `authentication_form = BibliotecaAuthenticationForm`: usa o formulário personalizado com textos em português.
- `redirect_authenticated_user = True`: se um utilizador já autenticado abrir `/login/`, o Django redireciona-o em vez de mostrar novamente a página de login.
- `get_success_url()` devolve a URL nomeada do catálogo, por isso um login bem-sucedido redireciona para o catálogo.

A criação real da sessão é feita pela `LoginView` do Django, não por código personalizado deste projecto.

Ficheiro relevante: `biblioteca/livros/views.py`.

## 5. O template de login envia credenciais de forma segura

A página de login contém um formulário POST normal que envia as credenciais para a rota de login.

Pontos importantes:

- `{% csrf_token %}` protege o POST contra ataques CSRF.
- O template mostra erros gerais do formulário e erros específicos dos campos.
- Se o Django fornecer um valor `next`, o template preserva-o num campo escondido. No estado atual do projecto, o login bem-sucedido é explicitamente redireccionado para o catálogo por `BibliotecaLoginView.get_success_url()`.

Ficheiro relevante: `biblioteca/livros/templates/livros/login.html`.

## 6. Depois do login, request.user controla a interface

Depois de um utilizador iniciar sessão, o middleware de sessão e autenticação do Django preenche `request.user` nos pedidos seguintes.

O template base usa esse valor para decidir o que aparece no cabeçalho:

- Utilizadores anónimos veem um link `Login`.
- Utilizadores autenticados veem um menu com o nome completo, ou o username quando não existe nome completo.
- O menu mostra o primeiro grupo do utilizador, se existir; se não existir grupo, mostra `membro` como perfil por defeito.
- O logout é feito por formulário POST, também protegido com `{% csrf_token %}`.

Ficheiro relevante: `biblioteca/livros/templates/livros/master.html`.

## 7. O logout delega na LogoutView do Django

`BibliotecaLogoutView` herda de `LogoutView` do Django.

A app define apenas `next_page` para a rota do catálogo. A view de logout do Django limpa os dados de autenticação da sessão, fazendo com que os pedidos seguintes voltem a ser anónimos.

Ficheiros relevantes:

- `biblioteca/livros/views.py`
- `biblioteca/livros/templates/livros/master.html`

## 8. A autorização é implementada com funções auxiliares, não com decorators do Django

Este projecto não usa `@login_required`, `LoginRequiredMixin`, `PermissionRequiredMixin` nem permissões Django ao nível do modelo para as páginas de livros.

Em vez disso, as regras ficam centralizadas em duas funções auxiliares:

- `can_view_book_detail(user)` devolve `True` quando `user.is_authenticated` é verdadeiro.
- `can_manage_books(user)` rejeita primeiro utilizadores anónimos e depois verifica se o utilizador pertence ao grupo `socio` ou `administrador`.

Os grupos que dão acesso de gestão estão definidos em `MANAGER_GROUPS = {'socio', 'administrador'}`.

Ficheiro relevante: `biblioteca/livros/views.py`.

## 9. O comportamento do catálogo muda conforme autenticação e grupo

`ListaLivrosView` adiciona duas flags de permissão ao contexto do template:

- `can_view_book_detail`
- `can_manage_books`

O template do catálogo usa essas flags da seguinte forma:

- Se `can_manage_books` for verdadeiro, mostra o botão `Novo livro`.
- Caso contrário, se o visitante for anónimo, mostra o botão `Registo Sócio`.
- A grelha de livros recebe `can_view_book_detail`; utilizadores autenticados recebem cartões clicáveis e informação de estado, enquanto visitantes anónimos recebem cartões estáticos sem estado/disponibilidade.

Ficheiros relevantes:

- `biblioteca/livros/views.py`
- `biblioteca/livros/templates/livros/livros.html`
- `biblioteca/livros/templates/livros/_book_grid.html`

## 10. Os detalhes do livro são protegidos em dispatch()

`LivroDetailView` sobrescreve `dispatch()`.

Todos os pedidos para a página de detalhe passam por `dispatch()` antes de o Django executar a lógica normal da `DetailView`. A view chama `can_view_book_detail(request.user)`:

- Utilizadores anónimos são redireccionados para o catálogo.
- Utilizadores autenticados continuam para a view normal de detalhe.

Dentro da página de detalhe, o contexto também inclui `can_manage_books`. O template usa essa flag para mostrar ou esconder as ações `Editar` e `Apagar`.

Ficheiros relevantes:

- `biblioteca/livros/views.py`
- `biblioteca/livros/templates/livros/livro_form.html`

## 11. Criar, editar e apagar são protegidos por grupo

As views de criação, edição e eliminação sobrescrevem `dispatch()` e chamam `can_manage_books(request.user)` antes de executar qualquer trabalho.

- `LivroCreateView`: utilizadores anónimos, utilizadores sem grupo e utilizadores no grupo `membro` são redireccionados para o catálogo.
- `LivroUpdateView`: utilizadores sem permissão são redireccionados para a página de detalhe do livro.
- `LivroDeleteView`: utilizadores sem permissão são redireccionados para a página de detalhe do livro.

Só utilizadores nos grupos `socio` ou `administrador` podem criar, editar ou apagar livros.

Ficheiro relevante: `biblioteca/livros/views.py`.

## 12. O registo/pedido de sócio valida dados, mas não cria utilizadores

O fluxo público de `Registo Sócio` não é o mesmo que criar uma conta Django.

`SubscriptionForm` importa o modelo `User` do Django e `validate_password`, mas apenas valida o pedido:

- `clean_username()` rejeita usernames que já existam na tabela de utilizadores do Django.
- `clean()` verifica se a palavra-passe e a confirmação coincidem.
- `clean()` também chama `validate_password(password, user=user)`, aplicando os validadores de palavra-passe configurados em `settings.py`.

Depois disso, `SubscriptionView.post()` mostra os dados de identificação submetidos e a mensagem de que a funcionalidade não está implementada e o utilizador não foi adicionado. A view não chama `User.objects.create_user()`.

Ficheiros relevantes:

- `biblioteca/livros/forms.py`
- `biblioteca/livros/views.py`
- `biblioteca/livros/templates/livros/subscription.html`

## 13. Os testes descrevem o comportamento esperado da autenticação

Os testes documentam e verificam o comportamento atual:

- A página de login apresenta labels em português para username e palavra-passe.
- Um login válido redireciona para o catálogo.
- Utilizadores anónimos veem um botão de login.
- Utilizadores autenticados veem username/perfil/logout no cabeçalho.
- O logout remove `_auth_user_id` da sessão.
- Visitantes não conseguem abrir detalhes de livros.
- Utilizadores autenticados sem grupo de gestão conseguem ver detalhes, mas não conseguem gerir livros.
- Utilizadores `membro` conseguem ver detalhes, mas não conseguem gerir livros.
- Utilizadores `socio` e `administrador` conseguem gerir livros.
- Um utilizador com vários grupos recebe a permissão mais alta, porque pertencer a `socio` é suficiente para passar em `can_manage_books()`.
- O registo de sócio valida usernames duplicados, mismatch de palavra-passe e validadores nativos do Django sem criar utilizador.

Ficheiro relevante: `biblioteca/livros/tests.py`.

## Exemplos de fluxo end-to-end

### Login bem-sucedido

1. O utilizador abre `/login/`.
2. `biblioteca/biblioteca/urls.py` inclui `livros.urls`.
3. `biblioteca/livros/urls.py` encaminha `login/` para `BibliotecaLoginView`.
4. `BibliotecaLoginView` renderiza `livros/login.html` com `BibliotecaAuthenticationForm`.
5. O utilizador submete username/password.
6. O `AuthenticationForm` herdado do Django valida as credenciais usando o sistema nativo de autenticação.
7. A `LoginView` herdada do Django guarda o id do utilizador autenticado na sessão.
8. `get_success_url()` redireciona para o catálogo.
9. Pedidos posteriores têm `request.user.is_authenticated == True`, porque o middleware de sessão e autenticação reconstrói o utilizador a partir da sessão.
10. `master.html`, `livros.html`, `_book_grid.html` e `livro_form.html` mudam o que mostram com base em `request.user` e nas flags de permissão das views.

### Visitante a abrir diretamente a URL de detalhe de um livro

1. O visitante abre `/livro/<isbn>/`.
2. A URL encaminha para `LivroDetailView`.
3. `dispatch()` chama `can_view_book_detail(request.user)`.
4. Para um utilizador anónimo, `user.is_authenticated` é falso.
5. A view redireciona para o catálogo em vez de mostrar a página de detalhe.

### `socio` a criar um livro

1. Um utilizador autenticado abre `/livro/novo/`.
2. A URL encaminha para `LivroCreateView`.
3. `dispatch()` chama `can_manage_books(request.user)`.
4. A função auxiliar verifica `request.user.groups.filter(name__in={'socio', 'administrador'}).exists()`.
5. Se o utilizador pertencer a `socio`, o pedido continua para o fluxo normal da `CreateView` do Django.
6. Numa submissão válida do formulário, `form_valid()` guarda o livro, adiciona uma mensagem de sucesso e redireciona para a página de detalhe do novo livro.
### Registo de sócio com dados inválidos
1. O visitante abre `/registo-socio/`.
2. A URL encaminha para `SubscriptionView`.
3. O visitante submete o formulário com um username já existente, ou com palavras-passe que não coincidem, ou com uma palavra-passe que falha nos validadores nativos do Django.
4. O formulário rejeita os dados e mostra os erros correspondentes no template de registo, sem criar nenhum utilizador na base de dados.
5. O visitante corrige os dados e submete novamente, desta vez com dados válidos.
6. O formulário valida os dados, mas a view mostra uma mensagem de que a funcionalidade de registo não está implementada e o utilizador não foi criado, sem criar nenhum utilizador na base de dados.
7. A aplicação simula o envio de um email com os dados submetidos, sem incluir a palavra-passe, e a mensagem de que o pedido de registo aguarda validação por um gestor da biblioteca. A mensagem é mostrada na consola do backend do _email sender_ configurado (Django).
