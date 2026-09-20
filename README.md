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

As sprints 0, 1 e 2 estão concluídas. A API permite enviar e consultar documentos PDF/TXT, gerar embeddings e recuperar trechos semanticamente relacionados em português, inglês e alemão. O endpoint de busca ainda faz apenas *retrieval*: a resposta final gerada por LLM será implementada em uma sprint posterior.

O desenvolvimento usa uma organização padrão configurada somente no backend. A autenticação e a identificação de organizações reais continuam pendentes; por isso o frontend não envia nem escolhe `organization_id`.

### Configuração da busca

- Preencha `OPENAI_API_KEY` apenas no `.env` local; nunca a inclua no frontend ou em commits.
- `LIMIAR_SIMILARIDADE=0.30` é o ponto inicial para recuperação multilíngue. Um limiar menor amplia a recuperação e pode trazer trechos menos precisos; ele deverá ser calibrado com documentos reais à medida que a base crescer.

## Endpoints disponíveis

- `GET /health`: confirma a API e o PostgreSQL.
- `POST /documents`: recebe um campo multipart chamado `arquivo` com PDF de até 5 páginas ou TXT, ambos limitados a 10 MB.
- `GET /documents`: lista os documentos enviados.
- `GET /documents/{id}`: retorna os metadados de um documento.
- `POST /search`: recupera trechos semanticamente relevantes, sem usar LLM.
- `POST /documents/{id}/reindex`: indexa documentos enviados antes do pipeline vetorial.

Use `http://localhost:8000/docs` para testar os endpoints interativamente.
