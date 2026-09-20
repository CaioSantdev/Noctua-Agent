# Noctua

Protótipo de agente de base de conhecimento multi-tenant.

## Pré-requisitos

- Docker Engine com Docker Compose v2

## Execução local

1. Copie `.env.example` para `.env` e ajuste os valores locais, se necessário.
2. Execute:

   ```bash
   docker compose up --build
   ```

3. Verifique o backend em `http://localhost:8000/health` e o frontend em `http://localhost:5173`. O healthcheck confirma a API e a conexão PostgreSQL.

## Estrutura

- `noctua_backend/`: API FastAPI e testes, com dependências geridas por `uv`.
- `noctua_frontend/`: aplicação React + TypeScript + Vite.
- `docker-compose.yml`: frontend, backend e PostgreSQL com pgvector.
- `noctua_database/init/`: inicialização da extensão `vector` em bancos novos.

## Escopo atual

As sprints 0 e 1 estão concluídas. A API permite enviar e consultar documentos PDF/TXT, mas autenticação, isolamento de tenants e IA ainda não foram implementados.

## Endpoints disponíveis

- `GET /health`: confirma a API e o PostgreSQL.
- `POST /documents`: recebe um campo multipart chamado `arquivo` com um PDF ou TXT de até 10 MB.
- `GET /documents`: lista os documentos enviados.
- `GET /documents/{id}`: retorna os metadados de um documento.

Use `http://localhost:8000/docs` para testar os endpoints interativamente.
