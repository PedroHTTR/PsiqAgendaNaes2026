import django_filters
from django.db.models import Q

from .models import Consulta, Paciente, Profissional


class PacienteFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(field_name='nome', lookup_expr='icontains')
    telefone = django_filters.CharFilter(field_name='telefone', lookup_expr='icontains')
    email = django_filters.CharFilter(field_name='email', lookup_expr='icontains')
    cpf = django_filters.CharFilter(field_name='cpf', lookup_expr='icontains')

    class Meta:
        model = Paciente
        fields = ['nome', 'telefone', 'email', 'cpf']


class ProfissionalFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(field_name='nome', lookup_expr='icontains')
    especialidade = django_filters.CharFilter(field_name='especialidade', lookup_expr='icontains')
    registro = django_filters.CharFilter(field_name='registro', lookup_expr='icontains')
    ativo = django_filters.BooleanFilter(field_name='ativo')

    class Meta:
        model = Profissional
        fields = ['nome', 'especialidade', 'registro', 'ativo']


class ConsultaFilter(django_filters.FilterSet):
    paciente = django_filters.ModelChoiceFilter(
        queryset=Paciente.objects.all(),
        field_name='paciente',
    )
    profissional = django_filters.ModelChoiceFilter(
        queryset=Profissional.objects.all(),
        field_name='profissional',
    )
    status = django_filters.ChoiceFilter(
        field_name='status',
        choices=Consulta.STATUS_CHOICES,
    )
    data = django_filters.DateFilter(field_name='data_hora', lookup_expr='date')
    busca = django_filters.CharFilter(method='filtrar_busca')

    class Meta:
        model = Consulta
        fields = ['paciente', 'profissional', 'status', 'data', 'busca']

    def filtrar_busca(self, queryset, name, value):
        return queryset.filter(
            Q(paciente__nome__icontains=value)
            | Q(profissional__nome__icontains=value)
            | Q(observacoes__icontains=value)
        )
