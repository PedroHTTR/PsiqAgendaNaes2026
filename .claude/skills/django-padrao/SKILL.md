---
name: django-padrao
description: Use ao criar ou alterar modelos, views, filtros, URLs, templates e testes Django neste projeto.
allowed-tools: Bash(python manage.py *), Bash(git diff *), Bash(git status *)
---

## Convenções

- Use migrations para alterações de modelos; não edite o banco manualmente.
- Prefira ListView/DetailView/CreateView/UpdateView/DeleteView para CRUD.
- Integre filtros com `django_filters.FilterSet` e mantenha parâmetros na paginação.
- Proteja dados por LoginRequiredMixin e PermissionRequiredMixin/grupos, não por `is_superuser`.
- Não coloque chaves ou credenciais em código, templates ou migrations.
- Execute `python manage.py check` e os testes focados após mudanças.
