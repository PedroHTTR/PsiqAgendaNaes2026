from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import JsonResponse
from django.utils.html import strip_tags
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
import markdown
import nh3

from .models import ConsumoIA, Conversa, Mensagem
from .services import chamar_ia


class ConversaListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Conversa
    template_name = "ia/conversa_list.html"
    permission_required = "ia.view_conversa"
    paginate_by = 30

    def get_queryset(self):
        return Conversa.objects.filter(usuario=self.request.user)


class ConversaDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Conversa
    template_name = "ia/conversa_detail.html"
    permission_required = "ia.view_conversa"

    def get_queryset(self):
        return Conversa.objects.filter(usuario=self.request.user)


class ConsumoIAListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = ConsumoIA
    template_name = "ia/consumo_list.html"
    permission_required = "ia.view_consumoia"
    paginate_by = 30

    def get_queryset(self):
        if self.request.user.has_perm("ia.view_all_consumo"):
            return ConsumoIA.objects.all()
        return ConsumoIA.objects.filter(usuario=self.request.user)


class ChatIAJsonView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "ia.usar_ia"

    @method_decorator(require_POST)
    def post(self, request, pk=None):
        mensagem = (request.POST.get("message") or "").strip()
        if not mensagem:
            return JsonResponse({"error": "Informe uma mensagem."}, status=400)

        conversa = None
        if pk:
            conversa = Conversa.objects.filter(
                pk=pk,
                usuario=request.user,
                ativa=True,
            ).first()
            if conversa is None:
                return JsonResponse({"error": "Conversa não encontrada."}, status=404)

        if not request.user.has_perm("ia.usar_ia"):
            raise PermissionDenied

        resposta = chamar_ia(
            strip_tags(mensagem),
            conversa=conversa,
            usuario=request.user,
        )
        resposta_html = nh3.clean(
            markdown.markdown(resposta),
            tags={
                "p", "br", "strong", "em", "ul", "ol", "li",
                "blockquote", "code", "pre", "a",
            },
            attributes={"a": {"href", "title"}},
        )

        if conversa is None:
            conversa = Conversa.objects.filter(usuario=request.user).latest("atualizada_em")

        if resposta:
            mensagem_assistente = conversa.mensagens.filter(
                remetente=Mensagem.Remetente.ASSISTENTE
            ).order_by("-criada_em").first()
            if mensagem_assistente is None:
                mensagem_assistente = Mensagem(
                    conversa=conversa,
                    remetente=Mensagem.Remetente.ASSISTENTE,
                )
            mensagem_assistente.conteudo = resposta_html
            mensagem_assistente.save()

        return JsonResponse({
            "conversation_id": conversa.pk,
            "response": resposta_html,
        })
