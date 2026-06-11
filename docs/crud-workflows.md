# Fluxos CRUD em Django

Este documento explica como funciona o fluxo CRUD em Django sobre uma base de dados SQLite, onde acontece cada passo e onde o código Python desencadeia as operações de manipulação de dados.

Em Django não se escreve instruções de SQL puro - como `INSERT`, `UPDATE` ou `DELETE` - manualmente. O ORM - ___Object-Relational Mapping___ - do Django gera esses comandos SQL a partir de chamadas Python como `QuerySet.get()`, `QuerySet.all()`, `ModelForm.save()` e `model.delete()`.

O ORM é uma camada de abstração para comandos DAO (___Data Access Object___) que traduz as operações escritas numa linguagem de programação (Python, no caso do presente projecto) em SQL. 

O uso de uma linguagem de programação é mais fluido e integrado com o resto do framework, uma vez que não requer o domínio da linguagem SQL, no entanto, o uso de mecanismos de abstracção como o ORM introduz complexidade adicional e menor transparência no código, decorrente dos '_tradutores_' entre a linguagem e o SQL. O processo, se mal compreendido ou aplicado, pode levar a erros, ineficiências ou dificuldades acrescidas para a manutenção e evolução do sistema.

Torna-se muito importante entender onde estão os equivalentes de `SELECT`, `INSERT`, `UPDATE` e `DELETE` para compreender o fluxo completo e tirar o maior proveito do mecanismo de ORM integrados com o Django.

O ORM de Django suporta múltiplos sistemas de gestão de base de dados, como PostgreSQL, MySQL/MariaDB e Oracle. MSSQL não é suportado nativamente pelo modelo ORM, necessita bibliotecas adicionais e modelos DAO nativos com SQL embutido. 
No exemplo utiliza-se SQLite pela simplicidade e facilidade de configuração, mas o fluxo CRUD explicado é aplicável a qualquer dos sistema indicados acima, com as diferenças específicas de cada SGBD a serem geridas pelo próprio ORM.

***Nota:***
- O foco deste documento é explicar o fluxo CRUD e o código Python para executar cada uma das operações. A gestão da base de dados está fora do âmbito da explicação.
- Esta exclusão de âmbito também permite que se mude o SGBD para outro compatível com ORM sem que isso afecte o conteúdo deste documento ou a funcionalidade do software desenvolvido.


## Configuração da base de dados

A base de dados está configurada em [`biblioteca/biblioteca/settings.py`](../biblioteca/biblioteca/settings.py):

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

Assim, a aplicação guarda os dados em:

```text
biblioteca/db.sqlite3
```

A app principal está registada em `INSTALLED_APPS`:

```python
'livros.apps.LivrosConfig',
```

## Modelos de dados

A estrutura da base de dados é descrita pelos modelos em [`biblioteca/livros/models.py`](../biblioteca/livros/models.py).

### `Editora`

```python
class Editora(models.Model):
    nipc = models.CharField(max_length=9, unique=True, primary_key=True)
    nome = models.CharField(max_length=100)
    contacto = models.CharField(max_length=100)
    morada = models.CharField(max_length=200)
```

Este modelo representa uma editora. A chave primária é `nipc`.

### `Livro`

```python
class Livro(models.Model):
    isbn = models.CharField(max_length=13, unique=True, primary_key=True)
    titulo = models.CharField(max_length=200)
    idioma = models.CharField(max_length=3)
    tipo = models.CharField(max_length=50)
    tema = models.CharField(max_length=100)
    editora = models.ForeignKey(Editora, to_field='nipc', on_delete=models.PROTECT)
    data_pub = models.DateField()
    original = models.BooleanField(default=True)
    status = models.CharField(...)
    data_add = models.DateTimeField(default=timezone.now)
```

Este modelo representa um livro. A chave primária é `isbn`.

O campo `editora` é uma chave estrangeira para `Editora`. A configuração `on_delete=models.PROTECT` significa que o Django impede a eliminação de uma `Editora` enquanto existirem livros associados a ela.

## Fluxo de URLs

Os pedidos entram primeiro no ficheiro de URLs ao nível do projecto:

[`biblioteca/biblioteca/urls.py`](../biblioteca/biblioteca/urls.py)

```python
urlpatterns = [
    path('', include('livros.urls', namespace='livros')),
    path('admin/', admin.site.urls),
    path('livros/', include(('livros.urls', 'livros'), namespace='livros_prefix')),
]
```

Depois são encaminhados para o ficheiro de URLs ao nível da app:

[`biblioteca/livros/urls.py`](../biblioteca/livros/urls.py)

```python
urlpatterns = [
    path('', views.HomeLivrosView.as_view(), name='home_livros'),
    path('catalogo/', views.ListaLivrosView.as_view(), name='lista_livros'),
    path('livro/novo/', views.LivroCreateView.as_view(), name='criar_livro'),
    path('livro/<str:isbn>/', views.LivroDetailView.as_view(), name='detalhe_livro'),
    path('livro/<str:isbn>/editar/', views.LivroUpdateView.as_view(), name='editar_livro'),
    path('livro/<str:isbn>/apagar/', views.LivroDeleteView.as_view(), name='apagar_livro'),
]
```

## Camada de serviços partilhada

A maior parte das leituras diretas e eliminações na base de dados está centralizada em [`biblioteca/livros/services.py`](../biblioteca/livros/services.py).

```python
class LivroService:
    @staticmethod
    def listar():
        return Livro.objects.select_related('editora').all()

    @staticmethod
    def obter_por_isbn(isbn):
        return Livro.objects.select_related('editora').get(isbn=isbn)

    @staticmethod
    def apagar(livro):
        livro.delete()
```

Este ficheiro é importante porque contém as chamadas ORM explícitas mais claras:

| Chamada ORM em Python | Equivalente SQL |
|---|---|
| `Livro.objects.select_related('editora').all()` | `SELECT ... FROM livros_livro ...` |
| `Livro.objects.select_related('editora').get(isbn=isbn)` | `SELECT ... WHERE isbn = ?` |
| `livro.delete()` | `DELETE FROM livros_livro WHERE isbn = ?` |

## Camada de formulários

A criação e a actualização usam ambas [`biblioteca/livros/forms.py`](../biblioteca/livros/forms.py).

```python
class LivroForm(forms.ModelForm):
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
```

Como a classe é um `ModelForm` (`forms.ModelForm` na declaração da classe indica que é um formulário baseado - herda de - em modelo; a linha `model = Livro` define o modelo associado ao formulário), o Django sabe converter os dados enviados pelo formulário HTML numa instância do modelo `Livro`.

Apesar dos automatismos, a lista de campos tem que ser escrita em código e tem que ter correspondência exacta com a definição do modelo associado. O Django não consegue adivinhar quais os campos que devem ser incluídos, nem consegue lidar com campos que não estejam definidos no modelo ou que nele existam mas não sejam declarados no formulário.

O mesmo formulario e usado para:

- criar um novo `Livro`
- atualizar um `Livro` existente

Durante a actualização, o campo ISBN fica desactivado:

```python
if readonly_isbn:
    self.fields['isbn'].disabled = True
```

Isto impede a alteração da chave primária depois de o livro já ter sido criado.

## Fluxo READ: listar livros

Rota:

```text
GET /catalogo/
```

Mapeamento do URL:

[`biblioteca/livros/urls.py`](../biblioteca/livros/urls.py)

```python
path('catalogo/', views.ListaLivrosView.as_view(), name='lista_livros')
```

View:

[`biblioteca/livros/views.py`](../biblioteca/livros/views.py)

```python
class ListaLivrosView(LivroListMixin, ListView):
    template_name = 'livros/livros.html'
```

`ListaLivrosView` usa `LivroListMixin`:

```python
class LivroListMixin:
    model = Livro
    context_object_name = 'livros'

    def get_queryset(self):
        return LivroService.listar()
```

A consulta à base de dados acontece em `LivroService.listar()`:

```python
return Livro.objects.select_related('editora').all()
```

Equivalente SQL:

```sql
SELECT ...
FROM livros_livro
JOIN livros_editora ON ...
ORDER BY titulo;
```
`select_related()` é um mecanismo ORM do Django para fazer referência - `[INNER] JOIN` - a uma tabela associada.

_o query SQL real do código é mais extenso e complexo, mas o exemplo reduzido serve para  mostrar o funcionamento geral_

O template é [`biblioteca/livros/templates/livros/livros.html`](../biblioteca/livros/templates/livros/livros.html).

que inclui a grelha de livros:

```django
{% include 'livros/_book_grid.html' with grid_label='Catalogo de livros' %}
```
ou seja, a grelha será carregada dentro do template principal, como se dela fizesse parte.

O template da grelha é definido num ficheiro separado para ser reutilizável noutros contextos, como a página de resultados de pesquisa. É uma técnica comum em Django para evitar duplicação de código HTML e manter a consistência visual. O truque está no ```{% include (...) %}```

O template da grelha é [`biblioteca/livros/templates/livros/_book_grid.html`](../biblioteca/livros/templates/livros/_book_grid.html):

```django
{% for livro in livros %}
  <a class="book-card" href="{% url 'livros:detalhe_livro' livro.isbn %}">
```

Cada cartão de livro liga à página de detalhe desse livro, por via do URL.

## Fluxo READ: detalhe do livro

Rota:

```text
GET /livro/<isbn>/
```

Mapeamento do URL:

```python
path('livro/<str:isbn>/', views.LivroDetailView.as_view(), name='detalhe_livro')
```

View:

```python
class LivroDetailView(DetailView):
    model = Livro
    template_name = 'livros/livro_form.html'
    context_object_name = 'livro'
    slug_field = 'isbn'
    slug_url_kwarg = 'isbn'

    def get_object(self, queryset=None):
        return LivroService.obter_por_isbn(self.kwargs['isbn'])
```
`[kwargs]` ou _keyword arguments_ são argumentos passados para a view através do URL. Neste caso, o URL tem um parâmetro `<str:isbn>` que captura o valor do ISBN do livro e o passa para a view como `self.kwargs['isbn']`.
Os `[kwargs]` são dicionários, pelo que têm que ser acedidos por chave. O Django não passa os parâmetros do URL como argumentos posicionais, mas sim como argumentos nomeados dentro de um dicionário.

`slug` é um termo genérico usado em Django para se referir a um identificador legível e amigável que é usado para identificar um objecto. Neste caso, o `slug_field` é `isbn`, o que significa que o valor do ISBN do livro será usado como identificador na URL. O `slug_url_kwarg` indica que o parâmetro do URL que contém o slug (neste caso, o ISBN) é chamado `isbn`. Ambos os valores `slug_field` e `slug_url_kwarg` são usados para configurar como a view de detalhe identifica o objecto a ser exibido com base no valor do ISBN passado na URL.

A consulta à base de dados acontece em `LivroService.obter_por_isbn()`:

```python
return Livro.objects.select_related('editora').get(isbn=isbn)
```

Equivalente SQL:

```sql
SELECT ...
FROM livros_livro
JOIN livros_editora ON ...
WHERE livros_livro.isbn = ?;
```

A página de detalhe usa o template partilhado [`biblioteca/livros/templates/livros/livro_form.html`](../biblioteca/livros/templates/livros/livro_form.html).

A view envia este contexto:

```python
context.update({
    'mode': 'detail',
    'page_title': 'Detalhes do livro',
    'submit_label': None,
})
```

O template verifica o modo:

```django
{% if mode == 'detail' %}
```

No modo de detalhe, a página mostra os dados do livro e botões de acção:

```django
<a class="button button-primary" href="{% url 'livros:editar_livro' livro.isbn %}">Editar</a>
<a class="button button-danger" href="{% url 'livros:apagar_livro' livro.isbn %}">Apagar</a>
```

## Fluxo CREATE: inserir um novo livro

Rotas:

```text
GET  /livro/novo/
POST /livro/novo/
```

Mapeamento do URL:

```python
path('livro/novo/', views.LivroCreateView.as_view(), name='criar_livro')
```

View:

```python
class LivroCreateView(CreateView):
    model = Livro
    form_class = LivroForm
    template_name = 'livros/livro_form.html'
```

### Pedido GET

Quando o utilizador abre `/livro/novo/`, o Django renderiza um `LivroForm` vazio usando:

[`biblioteca/livros/templates/livros/livro_form.html`](../biblioteca/livros/templates/livros/livro_form.html)

```django
<form method="post" novalidate>
    {% csrf_token %}
    ...
    <button class="button button-primary" type="submit">{{ submit_label }}</button>
</form>
```

### Pedido POST

Quando o utilizador submete o formulário, o Django valida os dados do formulário.

Se o formulário for válido, este método é executado:

```python
def form_valid(self, form):
    response = super().form_valid(form)
    messages.success(self.request, 'Livro inserido com sucesso.')
    return response
```

A linha importante é:

```python
response = super().form_valid(form)
```

Como esta classe estende a `CreateView` do Django, internamente o Django faz:

```python
self.object = form.save()
```

Como se trata de um novo objecto, `form.save()` cria uma nova linha na base de dados.

Equivalente SQL:

```sql
INSERT INTO livros_livro
(isbn, titulo, idioma, tipo, tema, editora_id, data_pub, original, status, data_add)
VALUES (...);
```

Depois da inserção, o utilizador é redireccionado para a página de detalhe:

```python
def get_success_url(self):
    return reverse_lazy('livros:detalhe_livro', kwargs={'isbn': self.object.isbn})
```
`reverse_lazy()` é uma função do Django que gera um URL a partir do nome da rota e dos parâmetros fornecidos. Neste caso, está a gerar o URL para a página de detalhe do livro recém-criado, usando o ISBN do livro como parâmetro.

## Fluxo UPDATE: editar um livro existente

Rotas:

```text
GET  /livro/<isbn>/editar/
POST /livro/<isbn>/editar/
```

Mapeamento do URL:

```python
path('livro/<str:isbn>/editar/', views.LivroUpdateView.as_view(), name='editar_livro')
```

View:

```python
class LivroUpdateView(UpdateView):
    model = Livro
    form_class = LivroForm
    template_name = 'livros/livro_form.html'
    context_object_name = 'livro'
    slug_field = 'isbn'
    slug_url_kwarg = 'isbn'
```

### Pedido GET

Primeiro, o Django carrega o livro existente:

```python
def get_object(self, queryset=None):
    return LivroService.obter_por_isbn(self.kwargs['isbn'])
```

Que, por sua vez, chama:

```python
Livro.objects.select_related('editora').get(isbn=isbn)
```

Equivalente SQL:

```sql
SELECT ...
FROM livros_livro
WHERE isbn = ?;
```

Depois, o Django renderiza o formulario já preenchido com os dados existentes do livro.

A view passa `readonly_isbn=True` para o formulario:

```python
def get_form_kwargs(self):
    kwargs = super().get_form_kwargs()
    kwargs['readonly_isbn'] = True
    return kwargs
```

O formulário usa esse parâmetro para desactivar o campo ISBN, evitando a alteração da chave primária:

```python
if readonly_isbn:
    self.fields['isbn'].disabled = True
```

### Pedido POST

Quando o utilizador submete alterações, o Django valida o formulario.

Se o formulário for válido, este método é executado:

```python
def form_valid(self, form):
    response = super().form_valid(form)
    messages.success(self.request, 'Livro atualizado com sucesso.')
    return response
```

Mais uma vez, a linha importante é:

```python
response = super().form_valid(form)
```

Como esta classe estende a `UpdateView` do Django, internamente o Django faz:

```python
self.object = form.save()
```

Como o formulario está associado a um objecto já existente na base de dados, `form.save()` atualiza a linha existente.

Equivalente SQL:

```sql
UPDATE livros_livro
SET titulo = ?,
    idioma = ?,
    tipo = ?,
    tema = ?,
    editora_id = ?,
    data_pub = ?,
    original = ?,
    status = ?
WHERE isbn = ?;
```

Depois da actualização, o utilizador é redireccionado para a página de detalhe:

```python
def get_success_url(self):
    return reverse_lazy('livros:detalhe_livro', kwargs={'isbn': self.object.isbn})
```

## Fluxo DELETE: remover um livro

Rotas:

```text
GET  /livro/<isbn>/apagar/
POST /livro/<isbn>/apagar/
```

Mapeamento do URL:

```python
path('livro/<str:isbn>/apagar/', views.LivroDeleteView.as_view(), name='apagar_livro')
```

View:

```python
class LivroDeleteView(View):
    template_name = 'livros/livro_confirm_delete.html'
```

Este projecto usa uma view de eliminação personalizada em vez da `DeleteView` genérica do Django. Esta view garante maior controlo sobre o processo, mostrando uma página de confirmação antes de eliminar o livro e uma mensagem de sucesso depois da eliminação.

### Pedido GET

Quando o utilizador abre o URL de eliminação, a view carrega o livro:

```python
def get_livro(self):
    return LivroService.obter_por_isbn(self.kwargs['isbn'])
```

Depois renderiza a página de confirmação:

```python
def get(self, request, *args, **kwargs):
    livro = self.get_livro()
    return render(request, self.template_name, {'livro': livro})
```

O template é [`biblioteca/livros/templates/livros/livro_confirm_delete.html`](../biblioteca/livros/templates/livros/livro_confirm_delete.html):

```django
<form method="post">
    {% csrf_token %}
    <button class="button button-danger" type="submit">Confirmar delete</button>
</form>
```

### Pedido POST

Quando o utilizador confirma a eliminação, este método é executado:

```python
def post(self, request, *args, **kwargs):
    livro = self.get_livro()
    titulo = livro.titulo
    LivroService.apagar(livro)
    messages.success(request, f'Livro "{titulo}" apagado com sucesso.')
    return redirect('livros:lista_livros')
```

A eliminação real na base de dados acontece em `LivroService.apagar()`:

```python
def apagar(livro):
    livro.delete()
```

Equivalente SQL:

```sql
DELETE FROM livros_livro
WHERE isbn = ?;
```

Depois de eliminar, o utilizador é redireccionado de volta para o catálogo:

```python
return redirect('livros:lista_livros')
```

## Resumo CRUD

| acção CRUD | URL | View | Template | Operação ORM | Equivalente SQL |
|---|---|---|---|---|---|
| Listar livros | `/catalogo/` | `ListaLivrosView` | `livros.html`, `_book_grid.html` | `Livro.objects.select_related('editora').all()` | `SELECT ...` |
| Detalhe do livro | `/livro/<isbn>/` | `LivroDetailView` | `livro_form.html` | `Livro.objects.select_related('editora').get(isbn=isbn)` | `SELECT ... WHERE isbn = ?` |
| Criar livro | `/livro/novo/` | `LivroCreateView` | `livro_form.html` | `form.save()` dentro de `super().form_valid(form)` | `INSERT INTO livros_livro ...` |
| Atualizar livro | `/livro/<isbn>/editar/` | `LivroUpdateView` | `livro_form.html` | `form.save()` dentro de `super().form_valid(form)` | `UPDATE livros_livro SET ... WHERE isbn = ?` |
| Apagar livro | `/livro/<isbn>/apagar/` | `LivroDeleteView` | `livro_confirm_delete.html` | `livro.delete()` | `DELETE FROM livros_livro WHERE isbn = ?` |

## Onde estao o `INSERT`, o `UPDATE` e o `DELETE`?

Nao existe nenhum ficheiro SQL bruto com estes comandos.

Em vez disso:

- O `INSERT` acontece dentro de `LivroCreateView.form_valid()` quando `super().form_valid(form)` chama `form.save()`.
- O `UPDATE` acontece dentro de `LivroUpdateView.form_valid()` quando `super().form_valid(form)` chama `form.save()` num objecto existente.
- O `DELETE` acontece explicitamente em `LivroService.apagar()` através de `livro.delete()`.

Os ficheiros mais importantes para o CRUD são:

| Ficheiro | Finalidade |
|---|---|
| [`biblioteca/livros/models.py`](../biblioteca/livros/models.py) | Define as tabelas da base de dados através de modelos Django |
| [`biblioteca/livros/forms.py`](../biblioteca/livros/forms.py) | Define o `LivroForm` usado para criação e actualização |
| [`biblioteca/livros/views.py`](../biblioteca/livros/views.py) | Define as views CRUD e o fluxo dos pedidos |
| [`biblioteca/livros/services.py`](../biblioteca/livros/services.py) | Centraliza operações ORM explícitas de leitura/eliminação |
| [`biblioteca/livros/urls.py`](../biblioteca/livros/urls.py) | Mapeia URLs para views CRUD |
| [`biblioteca/livros/templates/livros/livro_form.html`](../biblioteca/livros/templates/livros/livro_form.html) | Template partilhado para detalhe/criação/actualização |
| [`biblioteca/livros/templates/livros/livro_confirm_delete.html`](../biblioteca/livros/templates/livros/livro_confirm_delete.html) | Template de confirmação de eliminação |
| [`biblioteca/livros/templates/livros/livros.html`](../biblioteca/livros/templates/livros/livros.html) | Template do catálogo/listagem |
| [`biblioteca/livros/templates/livros/_book_grid.html`](../biblioteca/livros/templates/livros/_book_grid.html) | Grelha reutilizável que liga livros às páginas de detalhe |
