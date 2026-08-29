from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from campeonato.models import Consulta, Paciente, Profissional


class Command(BaseCommand):
    help = 'Cria dados iniciais de demonstração para o consultório psiquiátrico.'

    def handle(self, *args, **options):
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@psiqagenda.com', 'is_staff': True, 'is_superuser': True},
        )
        if created:
            user.set_password('12345678')
            user.save()

        pacientes = [
            {'nome': 'Ana Souza', 'telefone': '11999990001', 'email': 'ana@exemplo.com', 'cpf': '12345678909'},
            {'nome': 'Bruno Costa', 'telefone': '11999990002', 'email': 'bruno@exemplo.com', 'cpf': '98765432100'},
            {'nome': 'Carla Mendes', 'telefone': '11999990003', 'email': 'carla@exemplo.com', 'cpf': '45678912300'},
            {'nome': 'Diego Almeida', 'telefone': '11999990004', 'email': 'diego@exemplo.com', 'cpf': '32165498700'},
        ]

        created_pacientes = []
        for data in pacientes:
            paciente, _ = Paciente.objects.get_or_create(
                cpf=data['cpf'],
                defaults={
                    'nome': data['nome'],
                    'telefone': data['telefone'],
                    'email': data['email'],
                },
            )
            created_pacientes.append(paciente)

        profissionais = [
            {'nome': 'Dr. Lucas Silva', 'especialidade': 'Psiquiatria', 'registro': 'CRM-12345', 'ativo': True},
            {'nome': 'Dra. Mariana Costa', 'especialidade': 'Psicologia Clínica', 'registro': 'CRP-56789', 'ativo': True},
            {'nome': 'Dr. Rafael Nunes', 'especialidade': 'Neurologia', 'registro': 'CRM-33445', 'ativo': True},
        ]

        created_profissionais = []
        for data in profissionais:
            profissional, _ = Profissional.objects.get_or_create(
                registro=data['registro'],
                defaults={
                    'nome': data['nome'],
                    'especialidade': data['especialidade'],
                    'ativo': data['ativo'],
                },
            )
            created_profissionais.append(profissional)

        base_time = timezone.now().replace(hour=9, minute=0, second=0, microsecond=0)
        consultas = [
            (0, created_pacientes[0], created_profissionais[0], 'AGENDADA', 'Consulta inicial'),
            (1, created_pacientes[1], created_profissionais[0], 'CONFIRMADA', 'Acompanhamento de rotina'),
            (2, created_pacientes[2], created_profissionais[1], 'AGENDADA', 'Avaliação psicológica'),
            (3, created_pacientes[3], created_profissionais[2], 'REALIZADA', 'Consulta neurológica'),
            (4, created_pacientes[0], created_profissionais[1], 'CONFIRMADA', 'Revisão de tratamento'),
            (5, created_pacientes[2], created_profissionais[0], 'AGENDADA', 'Retorno com prescrição'),
        ]

        for offset_days, paciente, profissional, status, observacoes in consultas:
            data_hora = base_time + timedelta(days=offset_days, hours=1)
            Consulta.objects.get_or_create(
                paciente=paciente,
                profissional=profissional,
                data_hora=data_hora,
                defaults={
                    'duracao_minutos': 50,
                    'status': status,
                    'observacoes': observacoes,
                    'criado_por': user,
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Seed concluído: {Paciente.objects.count()} pacientes, '
                f'{Profissional.objects.count()} profissionais e '
                f'{Consulta.objects.count()} consultas criadas.'
            )
        )
