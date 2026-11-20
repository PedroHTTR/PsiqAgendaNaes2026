---
name: ia-assistente
description: Use ao alterar serviços Gemini, chat AJAX, mensagens persistidas, consumo ou auditoria de IA.
allowed-tools: Bash(python manage.py *), Bash(git diff *), Bash(git status *)
---

## Convenções

- Centralize chamadas externas no wrapper `ia.services.chamar_ia`.
- Nunca registre a chave Gemini no código ou em logs.
- Persistir conversa e mensagens no banco antes e depois da resposta.
- Enviar à API somente o contexto necessário e no máximo as últimas cinco mensagens relevantes.
- Retornar chat AJAX com `JsonResponse` e sanitizar Markdown no backend.
- Cobrir erros, permissões por grupos e consumo/auditoria com testes mocks.
