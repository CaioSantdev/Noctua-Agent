# Noctua

## Estado atual

Sprint 1 concluída.

Esta primeira etapa cria a estrutura do monorepo, os containers de frontend, backend e PostgreSQL com pgvector habilitado, e os ambientes versionados por `uv` (`noctua_backend/uv.lock`) e npm (`noctua_frontend/package-lock.json`).

## Verificações executadas

- `docker compose config --quiet`
- Build das imagens de backend e frontend
- `pytest`: 2 testes aprovados para `GET /health`
- Build TypeScript/Vite do frontend
- `GET /health` retornando `{"status":"ok"}` com conexão real ao PostgreSQL
- PostgreSQL saudável com extensão `vector` habilitada
- Backend organizado nas camadas iniciais de `api`, `core`, `infrastructure`, `schemas` e `services`

## Sprint 1 - Gestão de documentos

- Upload, extração síncrona e consulta de PDF/TXT implementados.
- Persistência criada pela migration Alembic `20260920_01`.
- Arquivos são mantidos no volume Docker `documentos_data`.
- A autenticação ainda não existe; por isso a API não recebe `organization_id` do frontend.

## Ainda não implementado

- Upload e processamento de documentos
- Autenticação e multi-tenancy
- OpenAI, RAG, embeddings, Redis e workers
