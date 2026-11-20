from django.test import TestCase

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse
from unittest.mock import patch

from .models import ConsumoIA, Conversa, Mensagem, RequisicaoIA
from .services import chamar_ia


class ChamariaIAServiceTests(TestCase):
    @patch("ia.services.ia.GeminiClient")
    def test_chamar_ia_cria_conversa_mensagens_requisicao_e_consumo(self, gemini_class):
        usuario = get_user_model().objects.create_user("paciente", password="teste")
        chat = gemini_class.return_value.create_chat.return_value
        response = type(
            "Response",
            (),
            {
                "text": "Resposta de teste",
                "usage_metadata": type(
                    "Usage",
                    (),
                    {
                        "prompt_token_count": 12,
                        "candidates_token_count": 8,
                        "total_token_count": 20,
                    },
                )(),
            },
        )()
        chat.send_message.return_value = response

        texto = chamar_ia("Olá", usuario=usuario)

        self.assertEqual(texto, "Resposta de teste")
        self.assertEqual(Conversa.objects.count(), 1)
        self.assertEqual(Mensagem.objects.count(), 2)
        self.assertEqual(RequisicaoIA.objects.filter(status="SUCESSO").count(), 1)
        consumo = ConsumoIA.objects.get()
        self.assertEqual(consumo.tokens_entrada, 12)
        self.assertEqual(consumo.tokens_saida, 8)
        self.assertEqual(consumo.tokens_total, 20)

    @patch("ia.services.ia.GeminiClient")
    def test_chamar_ia_registra_erro_e_relança_excecao(self, gemini_class):
        usuario = get_user_model().objects.create_user("erro", password="teste")
        gemini_class.return_value.create_chat.return_value.send_message.side_effect = RuntimeError("falha")

        with self.assertRaisesRegex(RuntimeError, "falha"):
            chamar_ia("Teste", usuario=usuario)

        requisicao = RequisicaoIA.objects.get()
        self.assertEqual(requisicao.status, RequisicaoIA.Status.ERRO)
        self.assertIn("falha", requisicao.erro)


class PermissoesIAViewsTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user("grupoia", password="teste")
        self.grupo, _ = Group.objects.get_or_create(name="Usuário de IA")
        permissoes = Permission.objects.filter(
            codename__in=["view_conversa", "view_consumoia", "usar_ia"]
        )
        self.grupo.permissions.set(permissoes)
        self.usuario.groups.add(self.grupo)

    def test_usuario_do_grupo_pode_acessar_conversas_e_consumo(self):
        self.client.force_login(self.usuario)

        resposta_conversas = self.client.get(reverse("ia:conversa-list"))
        resposta_consumo = self.client.get(reverse("ia:consumo-list"))

        self.assertEqual(resposta_conversas.status_code, 200)
        self.assertEqual(resposta_consumo.status_code, 200)

    def test_usuario_sem_grupo_tem_acesso_negado(self):
        usuario = get_user_model().objects.create_user("semgrupo", password="teste")
        self.client.force_login(usuario)

        resposta = self.client.get(reverse("ia:conversa-list"))

        self.assertEqual(resposta.status_code, 403)


class ChatIAJsonTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user("chatia", password="teste")
        self.grupo, _ = Group.objects.get_or_create(name="Usuário de IA")
        permissoes = Permission.objects.filter(
            codename__in=["view_conversa", "usar_ia"]
        )
        self.grupo.permissions.set(permissoes)
        self.usuario.groups.add(self.grupo)
        self.conversa = Conversa.objects.create(
            usuario=self.usuario,
            modelo="gemini-3.5-flash-lite",
        )
        self.client.force_login(self.usuario)

    @patch("ia.views.chamar_ia")
    def test_endpoint_retorna_json_sanitizado_e_persiste_resposta(self, chamar):
        chamar.return_value = "**Olá** <script>alert('x')</script>"

        resposta = self.client.post(
            reverse("ia:chat-conversa", args=[self.conversa.pk]),
            {"message": "Olá"},
        )

        self.assertEqual(resposta.status_code, 200)
        payload = resposta.json()
        self.assertIn("<strong>Olá</strong>", payload["response"])
        self.assertNotIn("<script>", payload["response"])
        chamar.assert_called_once()

    def test_endpoint_rejeita_mensagem_vazia(self):
        resposta = self.client.post(
            reverse("ia:chat-conversa", args=[self.conversa.pk]),
            {"message": ""},
        )

        self.assertEqual(resposta.status_code, 400)
