from django.contrib import admin
from .models import Conversa, Mensagem, ConsumoIA, RequisicaoIA


class MensagemInline(admin.TabularInline):
    model = Mensagem
    extra = 0
    readonly_fields = ("remetente", "conteudo", "metadados", "criada_em")


@admin.register(Conversa)
class ConversaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "usuario", "modelo", "ativa", "atualizada_em")
    list_filter = ("ativa", "modelo")
    search_fields = ("titulo", "usuario__username")
    inlines = [MensagemInline]


@admin.register(Mensagem)
class MensagemAdmin(admin.ModelAdmin):
    list_display = ("conversa", "remetente", "criada_em")
    list_filter = ("remetente",)
    readonly_fields = ("conversa", "remetente", "conteudo", "metadados", "criada_em")


@admin.register(ConsumoIA)
class ConsumoIAAdmin(admin.ModelAdmin):
    list_display = ("usuario", "modelo", "tokens_total", "custo", "criado_em")
    list_filter = ("modelo",)
    readonly_fields = ("usuario", "conversa", "modelo", "tokens_entrada", "tokens_saida", "tokens_total", "custo", "criado_em")


@admin.register(RequisicaoIA)
class RequisicaoIAAdmin(admin.ModelAdmin):
    list_display = ("usuario", "modelo", "status", "duracao_ms", "criada_em")
    list_filter = ("status", "modelo")
    readonly_fields = (
        "usuario", "conversa", "modelo", "prompt", "resposta", "erro",
        "status", "duracao_ms", "criada_em", "concluida_em",
    )
