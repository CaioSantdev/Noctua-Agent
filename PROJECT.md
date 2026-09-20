# Noctua

## Estado atual

Sprint 2 concluída.

Esta primeira etapa cria a estrutura do monorepo, os containers de frontend, backend e PostgreSQL com pgvector habilitado, e os ambientes versionados por `uv` (`noctua_backend/uv.lock`) e npm (`noctua_frontend/package-lock.json`).

## Verificações executadas

- `docker compose config --quiet`
- Build das imagens de backend e frontend
- `pytest`: testes de saúde, documentos, chunking e isolamento de organização aprovados.
- Build TypeScript/Vite do frontend
- `GET /health` retornando `{"status":"ok"}` com conexão real ao PostgreSQL
- PostgreSQL saudável com extensão `vector` habilitada
- Backend organizado nas camadas de `api`, `core`, `infrastructure`, `models`, `repositories`, `schemas` e `services`

## Sprint 1 - Gestão de documentos

- Upload, extração síncrona e consulta de PDF/TXT implementados.
- Persistência criada pela migration Alembic `20260920_01`.
- Arquivos são mantidos no volume Docker `documentos_data`.
- Upload de PDF limitado a 5 páginas e de arquivos a 10 MB.
- A autenticação ainda não existe; por isso a API não recebe `organization_id` do frontend.

## Sprint 2 - Busca vetorial

- Organização padrão definida exclusivamente no backend para desenvolvimento.
- Extração, chunking com sobreposição, embeddings OpenAI e persistência em pgvector implementados.
- Reindexação de documentos já enviados disponível em `POST /documents/{id}/reindex`.
- Retrieval sem LLM validado com pgvector e filtro pela organização do backend.
- Consulta de PDF real validada em português, inglês e alemão. O limiar padrão é `0.30`, adequado como ponto inicial para recuperação multilíngue.

## Ainda não implementado

- Autenticação e multi-tenancy com identificação de organização real.
- Geração da resposta final e fontes por LLM.
- Interface React para envio, consulta e apresentação de fontes.
- Processamento assíncrono com workers e Redis.
