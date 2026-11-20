import os
import time
from pathlib import Path

from django.conf import settings
from django.utils.html import strip_tags
from django.utils import timezone

from campeonato.services.gemini_client import GeminiClient
from ia.models import ConsumoIA, Mensagem, RequisicaoIA


def _contexto_projeto() -> str:
    caminho = Path(__file__).resolve().parents[1] / "contexto_projeto.md"
    if caminho.exists():
        return caminho.read_text(encoding="utf-8")
    return ""


def _historico(conversa) -> str:
    if conversa is None:
        return ""
    mensagens = conversa.mensagens.exclude(
        remetente=Mensagem.Remetente.SISTEMA
    ).order_by("-criada_em")[:5]
    linhas = []
    for mensagem in reversed(list(mensagens)):
        papel = "Usuário" if mensagem.remetente == Mensagem.Remetente.USUARIO else "Assistente"
        linhas.append(f"{papel}: {strip_tags(mensagem.conteudo)}")
    return "\n".join(linhas)


def _usage_value(response, *names):
    usage = getattr(response, "usage_metadata", None)
    if usage is None:
        return 0
    for name in names:
        value = getattr(usage, name, None)
        if isinstance(value, int):
            return value
    return 0


def _usage(response):
    entrada = _usage_value(response, "prompt_token_count", "prompt_tokens")
    saida = _usage_value(response, "candidates_token_count", "completion_tokens")
    total = _usage_value(response, "total_token_count", "total_tokens")
    if not total:
        total = entrada + saida
    return entrada, saida, total


def chamar_ia(prompt, conversa=None, usuario=None, model=None, **kwargs):
    """Wrapper central para chamadas Gemini, persistência e consumo."""
    if usuario is None:
        usuario = kwargs.pop("user", None)
    if usuario is None:
        raise ValueError("usuario é obrigatório")
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("prompt não pode estar vazio")

    selected_model = model or os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    if conversa is None:
        from ia.models import Conversa

        conversa = Conversa.objects.create(
            usuario=usuario,
            modelo=selected_model,
            titulo=prompt.strip()[:80],
        )

    requisicao = RequisicaoIA.objects.create(
        usuario=usuario,
        conversa=conversa,
        modelo=selected_model,
        prompt=prompt,
    )
    Mensagem.objects.create(
        conversa=conversa,
        remetente=Mensagem.Remetente.USUARIO,
        conteudo=prompt,
    )

    inicio = time.monotonic()
    try:
        contexto = _contexto_projeto()
        historico = _historico(conversa)
        partes = [contexto]
        if historico:
            partes.append("Histórico recente da conversa:\n" + historico)
        partes.append("Nova solicitação:\n" + prompt)

        gemini = GeminiClient()
        chat = gemini.create_chat(model=selected_model)
        response = chat.send_message("\n\n".join(p for p in partes if p))
        texto = getattr(response, "text", None)
        if texto is None:
            texto = str(response)

        requisicao.status = RequisicaoIA.Status.SUCESSO
        requisicao.resposta = texto
        requisicao.duracao_ms = int((time.monotonic() - inicio) * 1000)
        requisicao.concluida_em = timezone.now()
        requisicao.save(update_fields=[
            "status", "resposta", "duracao_ms", "concluida_em"
        ])

        entrada, saida, total = _usage(response)
        ConsumoIA.objects.create(
            usuario=usuario,
            conversa=conversa,
            modelo=selected_model,
            tokens_entrada=entrada,
            tokens_saida=saida,
            tokens_total=total,
        )
        Mensagem.objects.create(
            conversa=conversa,
            remetente=Mensagem.Remetente.ASSISTENTE,
            conteudo=texto,
            metadados={"modelo": selected_model},
        )
        conversa.save(update_fields=["atualizada_em"])
        return texto
    except Exception as exc:
        requisicao.status = RequisicaoIA.Status.ERRO
        requisicao.erro = str(exc)
        requisicao.duracao_ms = int((time.monotonic() - inicio) * 1000)
        requisicao.concluida_em = timezone.now()
        requisicao.save(update_fields=[
            "status", "erro", "duracao_ms", "concluida_em"
        ])
        raise
