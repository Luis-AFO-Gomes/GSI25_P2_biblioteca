from django.contrib import admin

from .models import Autor, Editora, Livro, Tema, ZonasGeograficas
@admin.register(Editora)
class EditoraAdmin(admin.ModelAdmin):
    list_display = ('nipc', 'nome', 'contacto', 'morada')
    search_fields = ('nipc', 'nome')
    list_filter = ('nome',)

@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ('isbn', 'titulo', 'get_autores', 'idioma', 'tipo', 'tema', 'editora', 'data_pub', 'original', 'status', 'data_add')
    search_fields = ('isbn', 'titulo')
    list_filter = ('tipo', 'tema', 'status')

    @admin.display(description='Autores')
    def get_autores(self, obj):
        return obj.get_autores()

@admin.register(Tema)
class TemaAdmin(admin.ModelAdmin):  
    list_display = ('sigla', 'nome')
    search_fields = ('nome',)
    list_filter = ('nome',)

@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'data_nasc', 'nacionalidade')
    search_fields = ('id', 'nome')
    list_filter = ('nacionalidade',)   

@admin.register(ZonasGeograficas)
class ZonasGeograficasAdmin(admin.ModelAdmin):
    list_display = ('sigla', 'nome')
    search_fields = ('sigla', 'nome')
    list_filter = ('nome',)     


