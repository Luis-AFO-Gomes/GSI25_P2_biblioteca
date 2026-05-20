from django.contrib import admin

from .models import Livro

@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ('isbn', 'titulo', 'idioma', 'tipo', 'tema', 'editora', 'data_pub', 'original', 'status', 'data_add')
    search_fields = ('isbn', 'titulo')
    list_filter = ('tipo', 'tema', 'status')
    prepopulated_fields = {'tema': ('tipo',)}