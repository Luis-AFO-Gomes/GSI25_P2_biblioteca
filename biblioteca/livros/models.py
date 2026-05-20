from django.db import models
from django.utils import timezone

class Livro(models.Model):
    class Status(models.TextChoices):
        SUGERIDO = 'S', 'Sugerido'
        DISPONIVEL = 'D', 'Disponível'
        EMPRESTADO = 'E', 'Emprestado'
        RESERVADO = 'R', 'Reservado'
        RETIRADO = 'O', 'Retirado'
    isbn = models.CharField(max_length=13, unique=True, primary_key=True)
    titulo = models.CharField(max_length=200)
    idioma = models.CharField(max_length=3)
    tipo = models.CharField(max_length=50)
    tema = models.CharField(max_length=100)
    editora = models.CharField(max_length=100)
    data_pub = models.DateField()
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