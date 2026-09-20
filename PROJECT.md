# Noctua

## Estado atual

Sprint 3 concluída.

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

## Sprint 3 - RAG + LLM

- Endpoint `POST /chat` implementado com entrada `question` e saída `answer` e `sources`.
- O contexto é composto apenas por chunks recuperados para a organização configurada no backend e respeita `MAX_TOKENS_CONTEXTO`.
- A LLM recebe instruções para responder somente a partir do contexto e no idioma da pergunta.
- Fontes são geradas a partir dos metadados dos chunks e documentos; a LLM não define nomes de arquivo nem páginas.
- Sem contexto recuperado, o chat retorna a mensagem de insuficiência de informações sem chamar a LLM.
- A API Responses é usada com `store=False` para não armazenar respostas que contenham contexto de documentos.
- Fluxo integrado validado: pergunta, recuperação, contexto, LLM, resposta e fontes.

## Ainda não implementado

- Autenticação e multi-tenancy com identificação de organização real.
- Interface React para envio, consulta e apresentação de fontes.
- Processamento assíncrono com workers e Redis.
