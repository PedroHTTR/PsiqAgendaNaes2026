from django.db import models
from django.conf import settings


class Conversa(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversas_ia",
    )
    titulo = models.CharField(max_length=200, blank=True)
    modelo = models.CharField(max_length=100)
    ativa = models.BooleanField(default=True)
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-atualizada_em"]
        verbose_name = "conversa"
        verbose_name_plural = "conversas"
        permissions = [
            ("usar_ia", "Pode utilizar a inteligência artificial"),
        ]

    def __str__(self):
        return self.titulo or f"Conversa #{self.pk}"


class Mensagem(models.Model):
    class Remetente(models.TextChoices):
        USUARIO = "USUARIO", "Usuário"
        ASSISTENTE = "ASSISTENTE", "Assistente"
        SISTEMA = "SISTEMA", "Sistema"

    conversa = models.ForeignKey(
        Conversa,
        on_delete=models.CASCADE,
        related_name="mensagens",
    )
    remetente = models.CharField(max_length=20, choices=Remetente.choices)
    conteudo = models.TextField()
    metadados = models.JSONField(default=dict, blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["criada_em", "pk"]
        verbose_name = "mensagem"
        verbose_name_plural = "mensagens"

    def __str__(self):
        return f"{self.get_remetente_display()} - {self.conversa}"


class ConsumoIA(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="consumos_ia",
    )
    conversa = models.ForeignKey(
        Conversa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="consumos",
    )
    modelo = models.CharField(max_length=100)
    tokens_entrada = models.PositiveIntegerField(default=0)
    tokens_saida = models.PositiveIntegerField(default=0)
    tokens_total = models.PositiveIntegerField(default=0)
    custo = models.DecimalField(max_digits=12, decimal_places=6, default=0)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "consumo de IA"
        verbose_name_plural = "consumos de IA"
        permissions = [
            ("view_all_consumo", "Pode visualizar o consumo de todos os usuários"),
        ]

    def __str__(self):
        return f"{self.usuario} - {self.modelo} - {self.tokens_total} tokens"


class RequisicaoIA(models.Model):
    class Status(models.TextChoices):
        PENDENTE = "PENDENTE", "Pendente"
        SUCESSO = "SUCESSO", "Sucesso"
        ERRO = "ERRO", "Erro"

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="requisicoes_ia",
    )
    conversa = models.ForeignKey(
        Conversa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requisicoes",
    )
    modelo = models.CharField(max_length=100)
    prompt = models.TextField()
    resposta = models.TextField(blank=True)
    erro = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDENTE,
    )
    duracao_ms = models.PositiveIntegerField(default=0)
    criada_em = models.DateTimeField(auto_now_add=True)
    concluida_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-criada_em"]
        verbose_name = "requisição de IA"
        verbose_name_plural = "requisições de IA"

    def __str__(self):
        return f"{self.modelo} - {self.status} - {self.criada_em:%d/%m/%Y %H:%M}"
