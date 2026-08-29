
from django.urls import path
from .views import (
    PacienteCreate, PacienteUpdate, PacienteDelete, PacienteList, PacienteDetail,
    ProfissionalCreate, ProfissionalUpdate, ProfissionalDelete, ProfissionalList, ProfissionalDetail,
    ConsultaCreate, ConsultaUpdate, ConsultaDelete, ConsultaList, ConsultaDetail,
)

urlpatterns = [
    path('paciente/cadastrar/', PacienteCreate.as_view(), name='paciente-create'),
    path('paciente/atualizar/<int:pk>/', PacienteUpdate.as_view(), name='paciente-update'),
    path('paciente/excluir/<int:pk>/', PacienteDelete.as_view(), name='paciente-delete'),
    path('paciente/listar/', PacienteList.as_view(), name='paciente-list'),
    path('paciente/detalhar/<int:pk>/', PacienteDetail.as_view(), name='paciente-detail'),

    path('profissional/cadastrar/', ProfissionalCreate.as_view(), name='profissional-create'),
    path('profissional/atualizar/<int:pk>/', ProfissionalUpdate.as_view(), name='profissional-update'),
    path('profissional/excluir/<int:pk>/', ProfissionalDelete.as_view(), name='profissional-delete'),
    path('profissional/listar/', ProfissionalList.as_view(), name='profissional-list'),
    path('profissional/detalhar/<int:pk>/', ProfissionalDetail.as_view(), name='profissional-detail'),

    path('consulta/agendar/', ConsultaCreate.as_view(), name='consulta-create'),
    path('consulta/atualizar/<int:pk>/', ConsultaUpdate.as_view(), name='consulta-update'),
    path('consulta/excluir/<int:pk>/', ConsultaDelete.as_view(), name='consulta-delete'),
    path('consulta/listar/', ConsultaList.as_view(), name='consulta-list'),
    path('consulta/detalhar/<int:pk>/', ConsultaDetail.as_view(), name='consulta-detail'),
]
