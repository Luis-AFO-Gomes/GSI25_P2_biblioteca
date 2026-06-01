from django.db import models
from django.utils import timezone

class ZonasGeograficas(models.Model):
    sigla = models.CharField(max_length=3, unique=True, primary_key=True)
    nome = models.CharField(max_length=100)
    class Meta:
        ordering = ['nome']
        indexes = [
            models.Index(fields=['sigla']),
            models.Index(fields=['nome']),
        ]

    def __str__(self):
        return self.nome

class Editora(models.Model):
    nipc = models.CharField(max_length=9, unique=True, primary_key=True)
    nome = models.CharField(max_length=100)
    contacto = models.CharField(max_length=100)
    morada = models.CharField(max_length=200)
    class Meta:
        ordering = ['nipc']
        indexes = [
            models.Index(fields=['nipc']),
            models.Index(fields=['nome']),
        ]

    def __str__(self):
        return self.nome

class Tema(models.Model):
    sigla = models.CharField(max_length=6, unique=True, primary_key=True)
    nome = models.CharField(max_length=100)
    class Meta:
        ordering = ['nome']
        indexes = [
            models.Index(fields=['nome']),
            models.Index(fields=['sigla']),
        ]

    def __str__(self):
        return self.nome
    
class Autor(models.Model):
    id = models.CharField(max_length=12, unique=True, primary_key=True)
    nome = models.CharField(max_length=100)
    data_nasc = models.DateField(blank=True, null=True)
    nacionalidade = models.ForeignKey(ZonasGeograficas, to_field='sigla', on_delete=models.PROTECT)
    class Meta:
        ordering = ['nome']
        indexes = [
            models.Index(fields=['nome']),
        ]

    def __str__(self):
        return self.nome    

class Livro(models.Model):
    class Status(models.TextChoices):
        SUGERIDO = 'S', 'Sugerido'
        DISPONIVEL = 'D', 'Disponível'
        EMPRESTADO = 'E', 'Emprestado'
        RESERVADO = 'R', 'Reservado'
        RETIRADO = 'O', 'Retirado'
    isbn = models.CharField(max_length=13, unique=True, primary_key=True)
    titulo = models.CharField(max_length=200)
    autor = models.ManyToManyField(Autor)
    idioma = models.CharField(max_length=3)
    tipo = models.CharField(max_length=50)
    tema = models.ForeignKey(Tema, to_field='sigla', on_delete=models.PROTECT)
    editora = models.ForeignKey(Editora, to_field='nipc', on_delete=models.PROTECT)
    data_pub = models.DateField(null=True, blank=True)
    original = models.BooleanField(default=True)
    status = models.CharField(
        max_length=1,
        choices=Status.choices,
        default=Status.DISPONIVEL,
    )
    data_add = models.DateTimeField(default=timezone.now)
    objects = models.Manager()          # gestor de modelos padrão
    class Meta:
        ordering = ['titulo']
        indexes = [
            models.Index(fields=['titulo']),
            models.Index(fields=['tipo']),
            models.Index(fields=['tema']),
        ]

    def __str__(self):
        return self.titulo
    
    def get_autores(self):
        return ", ".join(author.nome for author in self.autor.all())
