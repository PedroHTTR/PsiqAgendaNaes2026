# AGENTS.md

## Estrutura

- `campeonato/`: domínio clínico e CRUD de pacientes, profissionais e consultas.
- `website/`: páginas públicas e templates compartilhados.
- `ia/`: arquitetura independente de assistente Gemini, conversas, consumo e auditoria.
- `naes2026/`: configuração central do projeto Django.

## Convenções

- Use Django 5.2 e templates existentes em `website/modelo2.html`.
- Filtros paginados devem usar `django_filters.FilterSet` e preservar o query string.
- Acesso administrativo deve usar grupos/permissões Django.
- Chaves e segredos devem vir de variáveis de ambiente; `.env` não deve ser versionado.
- Dados da IA são persistidos em `Conversa`, `Mensagem`, `ConsumoIA` e `RequisicaoIA`.
- Execute `python manage.py check` e testes após alterações.
