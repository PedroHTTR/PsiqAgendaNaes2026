from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Consulta, Paciente, Profissional


class ConsultaSchedulingTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='admin',
            password='12345678',
        )
        self.paciente = Paciente.objects.create(
            nome='Ana Souza',
            telefone='11999999999',
            email='ana@example.com',
            cpf='12345678909',
        )
        self.profissional = Profissional.objects.create(
            nome='Dr. Lucas Silva',
            especialidade='Psiquiatria',
            registro='CRM-12345',
            ativo=True,
        )

    def test_consulta_valida_pode_ser_agendada(self):
        data_hora = timezone.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=2)
        consulta = Consulta(
            paciente=self.paciente,
            profissional=self.profissional,
            data_hora=data_hora,
            duracao_minutos=50,
            status='AGENDADA',
            observacoes='Primeira consulta',
            criado_por=self.user,
        )

        consulta.full_clean()
        consulta.save()

        self.assertEqual(Consulta.objects.count(), 1)
        self.assertEqual(consulta.status, 'AGENDADA')

    def test_consulta_nao_pode_sobrepor_horario_do_mesmo_profissional(self):
        data_inicial = timezone.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=3)
        Consulta.objects.create(
            paciente=self.paciente,
            profissional=self.profissional,
            data_hora=data_inicial,
            duracao_minutos=50,
            status='AGENDADA',
            observacoes='Consulta inicial',
            criado_por=self.user,
        )

        conflito = Consulta(
            paciente=self.paciente,
            profissional=self.profissional,
            data_hora=data_inicial + timedelta(minutes=30),
            duracao_minutos=50,
            status='AGENDADA',
            observacoes='Consulta conflitante',
            criado_por=self.user,
        )

        with self.assertRaises(ValidationError):
            conflito.full_clean()

    def test_consulta_cancelada_nao_bloqueia_agendamento(self):
        data_inicial = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=4)
        Consulta.objects.create(
            paciente=self.paciente,
            profissional=self.profissional,
            data_hora=data_inicial,
            duracao_minutos=50,
            status='CANCELADA',
            observacoes='Consulta cancelada',
            criado_por=self.user,
        )

        nova_consulta = Consulta(
            paciente=self.paciente,
            profissional=self.profissional,
            data_hora=data_inicial + timedelta(minutes=30),
            duracao_minutos=50,
            status='AGENDADA',
            observacoes='Nova consulta',
            criado_por=self.user,
        )

        nova_consulta.full_clean()
        nova_consulta.save()

        self.assertEqual(Consulta.objects.filter(status='AGENDADA').count(), 1)

    def test_consulta_list_filtra_por_status_e_data(self):
        self.client.force_login(self.user)

        paciente_2 = Paciente.objects.create(
            nome='Bruno Costa',
            telefone='11988888888',
            email='bruno@example.com',
            cpf='98765432100',
        )

        data_1 = timezone.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=5)
        data_2 = data_1 + timedelta(days=1)

        Consulta.objects.create(
            paciente=self.paciente,
            profissional=self.profissional,
            data_hora=data_1,
            duracao_minutos=50,
            status='AGENDADA',
            observacoes='Primeira agenda',
            criado_por=self.user,
        )
        Consulta.objects.create(
            paciente=paciente_2,
            profissional=self.profissional,
            data_hora=data_2,
            duracao_minutos=50,
            status='CONFIRMADA',
            observacoes='Consulta confirmada',
            criado_por=self.user,
        )

        response_status = self.client.get(reverse('consulta-list'), {'status': 'AGENDADA'})
        self.assertEqual(len(response_status.context['object_list']), 1)
        self.assertEqual(response_status.context['object_list'][0].status, 'AGENDADA')

        response_data = self.client.get(reverse('consulta-list'), {'data': data_1.date().isoformat()})
        self.assertEqual(len(response_data.context['object_list']), 1)
        self.assertEqual(response_data.context['object_list'][0].data_hora.date(), data_1.date())

    def test_seed_clinic_creates_demo_data(self):
        call_command('seed_clinic')

        self.assertGreaterEqual(Paciente.objects.count(), 3)
        self.assertGreaterEqual(Profissional.objects.count(), 3)
        self.assertGreaterEqual(Consulta.objects.count(), 5)
