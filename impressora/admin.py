from django.contrib import admin
from .models import Impressora, Setor

@admin.register(Impressora)
class ImpressoraAdmin(admin.ModelAdmin):
    list_display = ('nome', 'nome_sistema', 'ativa')
    search_fields = ('nome', 'nome_sistema')
    list_filter = ('ativa',)

@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'impressora')
    search_fields = ('nome',)
    list_filter = ('impressora',)
