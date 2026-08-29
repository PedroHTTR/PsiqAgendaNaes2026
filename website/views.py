from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from campeonato.models import Paciente, Profissional, Consulta

# import timezone do django
from django.utils import timezone


class CadastroView(CreateView):
    form_class = UserCreationForm
    template_name = "campeonato/form.html"
    success_url = reverse_lazy("login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = "Criar conta"
        context["botao"] = "Criar conta"
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Conta criada com sucesso. Faça login para continuar.")
        return response


class IndexView(TemplateView):
    template_name = "website/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        agora = timezone.now()

        context["total_pacientes"] = Paciente.objects.count()
        context["total_profissionais"] = Profissional.objects.count()
        context["total_consultas"] = Consulta.objects.count()
        context["consultas_hoje"] = Consulta.objects.filter(data_hora__date=agora.date()).count()
        context["consultas_agendadas"] = Consulta.objects.filter(status='AGENDADA').count()
        context["consultas_confirmadas"] = Consulta.objects.filter(status='CONFIRMADA').count()
        context["consultas_realizadas"] = Consulta.objects.filter(status='REALIZADA').count()

        context["consultas_proximas"] = Consulta.objects.filter(
            data_hora__gte=agora
        ).order_by("data_hora")[:5]

        context["consultas_hoje_lista"] = Consulta.objects.filter(
            data_hora__date=agora.date()
        ).order_by("data_hora")[:5]

        context["profissionais_ativos"] = Profissional.objects.filter(ativo=True)[:3]

        return context

class ContatoView(TemplateView):
    template_name = "website/contato.html"
    
class SobreView(TemplateView):
    template_name = "website/sobre.html"