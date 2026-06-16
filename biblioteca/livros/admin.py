from django.contrib import admin

from .models import Arvore


@admin.register(Arvore)
class ArvoreAdmin(admin.ModelAdmin):

    list_display = (
        'nome',
        'tipo',
        'altura',
        'preco',
        'stock',
        'pais_origem'
    )

    search_fields = (
        'nome',
        'tipo',
        'pais_origem'
    )

    list_filter = (
        'tipo',
        'pais_origem'
    )
