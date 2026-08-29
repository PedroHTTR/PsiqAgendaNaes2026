from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class NavigationRegressionTests(TestCase):
    def test_homepage_does_not_render_empty_links(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

        html = response.content.decode('utf-8')
        self.assertNotIn('href=""', html)
        self.assertNotIn("href='#'", html)
        self.assertNotIn('href="#"', html)

    def test_anonymous_homepage_does_not_expose_protected_create_links(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

        html = response.content.decode('utf-8')
        self.assertNotIn(reverse('paciente-create'), html)
        self.assertNotIn(reverse('profissional-create'), html)
        self.assertNotIn(reverse('consulta-create'), html)
        self.assertIn(reverse('login'), html)
        self.assertIn(reverse('cadastro'), html)

    def test_registration_page_is_public(self):
        response = self.client.get(reverse('cadastro'))
        self.assertEqual(response.status_code, 200)
        html = response.content.decode('utf-8')
        self.assertIn('Criar conta', html)
        self.assertIn('username', html.lower())

    def test_authenticated_navigation_exposes_consultorio_routes(self):
        user = get_user_model().objects.create_user(username='admin', password='12345678')
        self.client.force_login(user)

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

        html = response.content.decode('utf-8')
        self.assertIn(reverse('paciente-create'), html)
        self.assertIn(reverse('profissional-create'), html)
        self.assertIn(reverse('consulta-create'), html)
        self.assertIn(reverse('paciente-list'), html)
        self.assertIn(reverse('profissional-list'), html)
        self.assertIn(reverse('consulta-list'), html)
