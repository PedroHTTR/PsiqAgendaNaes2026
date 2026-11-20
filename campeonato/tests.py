from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from unittest.mock import patch

from .models import Consulta, Paciente, Profissional
from .services.gemini_client import GeminiClient


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


class DjangoFilterTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='filtro',
            password='12345678',
        )
        self.client.force_login(self.user)

    def test_paciente_filtra_por_nome_e_cpf_em_combinacao(self):
        ana = Paciente.objects.create(
            nome='Ana Souza',
            telefone='11911111111',
            email='ana@example.com',
            cpf='11111111111',
        )
        Paciente.objects.create(
            nome='Ana Costa',
            telefone='11922222222',
            email='ana.costa@example.com',
            cpf='22222222222',
        )

        response = self.client.get(
            reverse('paciente-list'),
            {'nome': 'Souza', 'cpf': '111111'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('filter', response.context)
        self.assertQuerySetEqual(response.context['object_list'], [ana])

    def test_profissional_filtra_nome_especialidade_e_ativo(self):
        ativo = Profissional.objects.create(
            nome='Dra. Helena Lima',
            especialidade='Psicologia',
            registro='CRP-123',
            ativo=True,
        )
        Profissional.objects.create(
            nome='Dr. Paulo Lima',
            especialidade='Psiquiatria',
            registro='CRM-123',
            ativo=False,
        )

        response = self.client.get(
            reverse('profissional-list'),
            {'nome': 'Helena', 'especialidade': 'Psico', 'ativo': 'true'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context['object_list'], [ativo])

    def test_consulta_combina_status_profissional_e_busca(self):
        paciente = Paciente.objects.create(
            nome='Marina Dias',
            telefone='11933333333',
            cpf='33333333333',
        )
        profissional = Profissional.objects.create(
            nome='Dr. Miguel Nunes',
            especialidade='Psiquiatria',
            ativo=True,
        )
        outro_profissional = Profissional.objects.create(
            nome='Dra. Bia',
            especialidade='Psicologia',
            ativo=True,
        )
        consulta = Consulta.objects.create(
            paciente=paciente,
            profissional=profissional,
            data_hora=timezone.now().replace(hour=14, minute=0, second=0, microsecond=0) + timedelta(days=2),
            duracao_minutos=50,
            status='CONFIRMADA',
            observacoes='Retorno urgente',
            criado_por=self.user,
        )
        Consulta.objects.create(
            paciente=paciente,
            profissional=outro_profissional,
            data_hora=timezone.now().replace(hour=15, minute=0, second=0, microsecond=0) + timedelta(days=2),
            duracao_minutos=50,
            status='AGENDADA',
            observacoes='Retorno urgente',
            criado_por=self.user,
        )

        response = self.client.get(
            reverse('consulta-list'),
            {
                'status': 'CONFIRMADA',
                'profissional': str(profissional.pk),
                'busca': 'Marina',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context['object_list'], [consulta])

    def test_paginacao_mantem_parametros_get(self):
        for index in range(31):
            Paciente.objects.create(
                nome=f'Paciente {index}',
                telefone=f'119{index:08d}',
                cpf=f'{index:011d}',
            )

        response = self.client.get(
            reverse('paciente-list'),
            {'nome': 'Paciente', 'page': '2'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(response.context['page_obj'].number, 2)
        self.assertContains(response, 'nome=Paciente')
        self.assertContains(response, 'page=1')


class GeminiClientTests(TestCase):
    @patch("campeonato.services.gemini_client.genai.Client")
    @patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}, clear=True)
    def test_inicializa_cliente_com_chave_configurada(self, client_constructor):
        gemini_client = GeminiClient()

        client_constructor.assert_called_once_with(api_key="test-key")
        self.assertIs(gemini_client.client, client_constructor.return_value)

    @patch("campeonato.services.gemini_client.load_dotenv")
    @patch.dict("os.environ", {}, clear=True)
    def test_falha_quando_chave_nao_esta_configurada(self, _load_dotenv):
        with self.assertRaisesRegex(RuntimeError, "GEMINI_API_KEY"):
            GeminiClient()

    @patch("campeonato.services.gemini_client.genai.Client")
    @patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}, clear=True)
    def test_cria_sessao_de_chat_com_modelo_padrao(self, client_constructor):
        chat = object()
        client_constructor.return_value.chats.create.return_value = chat
        gemini_client = GeminiClient()

        result = gemini_client.create_chat()

        client_constructor.return_value.chats.create.assert_called_once_with(
            model="gemini-3.5-flash-lite"
        )
        self.assertIs(result, chat)

    @patch("campeonato.services.gemini_client.genai.Client")
    @patch.dict(
        "os.environ",
        {"GEMINI_API_KEY": "test-key", "GEMINI_MODEL": "test-model"},
        clear=True,
    )
    def test_cria_sessao_com_modelo_da_configuracao(self, client_constructor):
        gemini_client = GeminiClient()

        gemini_client.create_chat()

        client_constructor.return_value.chats.create.assert_called_once_with(
            model="test-model"
        )

    @patch("campeonato.services.gemini_client.genai.Client")
    @patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}, clear=True)
    def test_envia_mensagens_sequenciais_e_retorna_texto(self, client_constructor):
        chat = client_constructor.return_value.chats.create.return_value
        chat.send_message.side_effect = [
            type("Response", (), {"text": "Resposta do turno 1"}),
            type("Response", (), {"text": "Resposta do turno 2"}),
        ]
        gemini_client = GeminiClient()
        chat_session = gemini_client.create_chat()

        first = gemini_client.send_message(chat_session, "Olá")
        second = gemini_client.send_message(chat_session, "Qual projeto?")

        self.assertEqual(first, "Resposta do turno 1")
        self.assertEqual(second, "Resposta do turno 2")
        self.assertEqual(chat.send_message.call_count, 2)
