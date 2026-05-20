## Parte III - Admin Site
- ponto prévio
  Caso ainda não te nha sido criado, definir admin/superuser
  No terminal, executar:

  ```python manage.py createsuperuser```

  O python irá solicitar nome de utilizador, email e palavra-passe, com confirmação.<br>
  Todos os campos são obrigatórios<br>
  Para testar a configuração, pode-se aceder ao site de administração em ```http://127.0.0.1:8000/admin``` e fazer login com as credenciais inseridas<br>
  ![alt text](image.png)
  Ajustar o endereço ao utilizado em ```runserver```</small>

### Criar uma classe personalizada 
- As classes/modelos são criadas em ```models.py``` dentro da pasta da App ('livros' no nosso exemplo):<br>
  Classe [Livro](.\biblioteca\livros\models.py)

  Elementos importantes na classe:
  1. ```models.«data type»``` indica tipo de dados do atributo
  2.  ```unique=True, primary_key=True``` indicam chave unica e chave primaria respectivamente
  3.  ```class Status(models.TextChoices):``` indica um tipo enumerado a utilizar como valores para um atributo da classe
    em ```SUGERIDO = 'S', 'Sugerido'```:<br>
    **SUGERIDO** indica o nome do valor;<br>
    **'S'** a chave de registo;<br> 
    **'Sugerido'** o valor do registo, utilizado para UI;<br>
  4. O valor enumerado é chamado por:
    ```
        status = models.CharField(
            max_length=1,
            choices=Status.choices,
            default=Status.DISPONIVEL,
        )
    ```
    onde:<br>
    ```status``` indica o nome do atributo;<br>
    ```max_length``` o tamanho <br>
    ```choices``` a lista de enumeração dos valores a utilizar - **Status**.choices. No exemplo, o nome do campo é igual ao da classe enumerada, mas isso não é obrigatório<br>
    ```default``` valor por defeito

  5. ```(default=timezone.now)``` define um valor por defeito para o atributo (neste caso, a data actual do sistema), caso um não seja indicado na inserção;
  6. ```Class Meta:``` define meta valores e comportamentos para a classe:
     1. ```ordering``` define ordenação padrão da lista a apresentar no UI padrão
     2. ```indexes``` define indices de ordenação da tabela 

### 'Migrar' o modelo para base de dados
Usando ORM, o python irá gerar a base de dados a partir dos modelos definidos para a App num processo semi-automático
1. gerar a migração:
```
python manage.py makemigrations livros
```
É gerado um ficheiro ```nnnn_«nome».py``` na pasta ```livros\migrations```<br>
O numero é incrementado a cada nova migração<br>
Não alterar nem apagar estes ficheiros, o python irá geri-los de acordo com as necessidades

2. validar o modelo de migração gerado
```
python manage.py sqlmigrate livros nnnn
```
3. aplicar a migração
```
python manage.py migrate
```
**Nota** este processo de migração tem que ser repetido a cada alteração relevante do modelo

### Registar a classe/***model*** na app de administração
Adicionar ao ficheiro ```livros\admin.py```:
```
from .models import Livro

@admin.register(Livro)
```
e adicionar uma vista personalizada para apresentação na página de administração
```
class LivroAdmin(admin.ModelAdmin):
    list_display = ('isbn', 'titulo', 'idioma', 'tipo', 'tema', 'editora', 'data_pub', 'original', 'status', 'data_add')
    search_fields = ('isbn', 'titulo')
    list_filter = ('tipo', 'tema', 'status')
    prepopulated_fields = {'tema': ('tipo',)}
```
onde:<br>
    ```list_display``` indica as colunas a apresentar, não tem que ser todos os atributos da classe<br>
    ```search_fields``` campos de pesquisa<br>
    ```list_filter``` campos ordenação<br>
    ```prepopulated_fields``` campos com preenchimento ligado, 'tema' é preenchido com valor de 'tipo', pode ser alterado<br>
Só neste ponto o site de administração apresentará a página de livros. No entanto, é necessário...

### Confirmar registo de URL de administração
Confirmar que na secção ```[urlpatterns]``` do ficheiro ```biblioteca\urls.py``` tem o registo:
```
path('admin/', admin.site.urls),
```
**ATENÇÃO** o registo é no ficheiro ```urls.py``` na root do projecto, não no da app