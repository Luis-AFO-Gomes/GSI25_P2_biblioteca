from django.db import models


class Arvore(models.Model):

    nome = models.CharField(max_length=100)

    tipo = models.CharField(max_length=50)

    altura = models.FloatField()

    preco = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    stock = models.IntegerField(default=0)

    pais_origem = models.CharField(max_length=100)

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return self.nome
