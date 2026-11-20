---
name: commit-padrao
description: Use sempre que for escrever a mensagem de um commit neste projeto — gera mensagens no padrão Conventional Commits, com resumo no imperativo e um corpo curto que descreve o que foi implementado, nunca apenas um rótulo genérico como "fix" ou "ajustes".
allowed-tools: Bash(git diff *), Bash(git status *), Bash(git log *)
---

## Mudanças pendentes

Antes de escrever a mensagem, rode e leia a saída (o Cursor não expande `!comando`):

```bash
git status
git diff --cached
git log -5 --oneline
```

Se não houver nada staged, informe isso e sugira `git add` — não invente mensagem.

O `git log -5` serve só para contexto do projeto (convenções de escopo, linguagem usada).
Não copie o formato de commits anteriores se eles forem genéricos — a mensagem gerada
segue as regras abaixo independentemente do estilo do histórico.

## Formato obrigatório

Escreva a mensagem de commit seguindo estas regras, sem exceção:

1. **Primeira linha**: `tipo(escopo): resumo no imperativo`, até 72 caracteres, sem ponto final. Tipos válidos: feat, fix, docs, style, refactor, perf, test, build, ci, chore.
2. **Linha em branco** depois do resumo.
3. **Corpo obrigatório se o diff tocar mais de um arquivo E passar de ~15 linhas no total**: escreva de 2 a 5 linhas ou bullets descrevendo concretamente o que foi implementado. Nomeie função, modelo, rota ou comportamento alterado. Nunca use "ajustes diversos", "melhorias" ou repita o resumo com outras palavras.
4. **Exceção ao corpo obrigatório**: se a mudança for autoexplicativa pelo resumo, como corrigir um typo, atualizar um link ou fazer bump de versão, o corpo pode ser omitido mesmo tocando vários arquivos ou passando de 15 linhas.
5. Se o diff misturar mudanças sem relação entre si, não invente uma mensagem que cubra as duas. Avise o usuário e sugira separar o staged em dois commits.
6. Nunca descreva algo que não esteja no diff staged mostrado.
7. Se o diff estiver vazio, informe que não há mudanças staged e sugira `git add`; não gere uma mensagem genérica.
8. **Documentos e IDs do projeto**: mudanças em `docs/` usam o nome do arquivo como escopo, por exemplo `docs(prd): ...`. Se a mudança cria ou altera requisito, regra, caso de uso ou tarefa (RF, RN, UC, T), cite o ID no resumo ou no corpo.

O commit só está correto se o `git log -1` mostrar o resumo e o corpo quando o corpo for exigido pela regra 3. Título sozinho não atende esta skill quando um corpo é exigido.

## Conteúdo do corpo

O corpo responde "o que mudou no código?", não "qual é o tema do commit".

- Cite nomes presentes no diff: função, classe, rota, template ou teste.
- Prefira bullets quando houver mais de uma mudança concreta.
- Não reescreva o título com sinônimos como "adiciona o pipeline", "implementa a funcionalidade" ou "inclui melhorias".

### Exemplo rejeitado

```text
feat(app): implementar analisador Flask de commits do GitHub

Adiciona o pipeline de validação, clone e extração, o relatório
com Plotly, os testes e o README.
```

Esse exemplo parafraseia o título e não identifica o que o diff criou.

### Exemplo correto

```text
feat(app): implementar analisador Flask de commits do GitHub

Cria Commit, FileChange e ReportData em models/commit.py.
Implementa parse_conventional_commit, parse_github_url,
clone_repository, extract_commits, build_report e cleanup_repo.
A rota POST /analisar orquestra o pipeline e renderiza report.html.
```
