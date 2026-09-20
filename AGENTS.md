# AGENTS.md

## Projeto

Agente de Base de Conhecimento com IA.

Stack: Python, FastAPI, React, TypeScript, PostgreSQL, pgvector, Docker e OpenAI.

Agno poderá ser utilizado apenas quando houver justificativa.

## Arquitetura

Separar `routes`, `schemas`, `models`, `repositories`, `services`, `infrastructure` e `tests`.

- Rotas não contêm regras de negócio.
- Persistência passa por repositories.
- RAG fica na camada de services.

## Segurança

- Nunca colocar secrets no código.
- Nunca expor `OPENAI_API_KEY` no frontend.
- Nunca confiar em `organization_id` enviado pelo frontend.
- Toda busca deve respeitar o tenant.

## Qualidade

Antes de concluir uma tarefa, executar os testes aplicáveis, verificar erros e isolamento de tenant, explicar as alterações e atualizar `PROJECT.md`.

## Idioma e identidade

- O nome oficial do projeto é `Noctua`.
- Usar português em comentários, docstrings, mensagens de commit, documentação e nomes de domínio quando isso não conflitar com convenções técnicas da stack.

## Escopo

Não implementar sprints futuras sem autorização explícita. Não criar abstrações sem necessidade nem adicionar dependências sem explicar.
