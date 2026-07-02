from django.contrib import admin

from .models import Atividade, Categoria, Viagem


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    search_fields = ("nome",)


class AtividadeInline(admin.TabularInline):
    model = Atividade
    extra = 1


@admin.register(Viagem)
class ViagemAdmin(admin.ModelAdmin):
    list_display = ("titulo", "destino", "usuario", "data_inicio", "data_fim", "publica")
    list_filter = ("publica", "destino")
    search_fields = ("titulo", "destino")
    inlines = [AtividadeInline]


@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    list_display = ("nome", "viagem", "categoria", "data_hora", "custo_estimado")
    list_filter = ("categoria",)
