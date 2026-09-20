# Noctua

Protótipo de agente de base de conhecimento multi-tenant.

## Pré-requisitos

- Docker Engine com Docker Compose v2

## Execução local

1. Copie `.env.example` para `.env` e ajuste os valores locais, se necessário.
   Gere e informe um segredo JWT local antes de subir a aplicação:

   ```bash
   openssl rand -hex 32
   ```

   Use o valor gerado em `JWT_SECRET` no `.env`. Nunca versione esse arquivo.
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

As sprints 0, 1 e 2 estão concluídas. A Sprint 3 adiciona o chat RAG: a API recupera trechos semanticamente relacionados em português, inglês e alemão, limita o contexto por tokens e gera uma resposta fundamentada por LLM com fontes.

O desenvolvimento usa uma organização padrão configurada somente no backend. A autenticação e a identificação de organizações reais continuam pendentes; por isso o frontend não envia nem escolhe `organization_id`.

### Configuração da busca

- Preencha `OPENAI_API_KEY` apenas no `.env` local; nunca a inclua no frontend ou em commits.
- `LIMIAR_SIMILARIDADE=0.30` é o ponto inicial para recuperação multilíngue. Um limiar menor amplia a recuperação e pode trazer trechos menos precisos; ele deverá ser calibrado com documentos reais à medida que a base crescer.

## Endpoints disponíveis

- `GET /health`: confirma a API e o PostgreSQL.
- `POST /auth/register`: cria uma organização e seu primeiro usuário.
- `POST /auth/login`: autentica um usuário e retorna um JWT.
- `POST /documents`: recebe um campo multipart chamado `arquivo` com PDF de até 5 páginas ou TXT, ambos limitados a 10 MB.
- `GET /documents`: lista os documentos enviados.
- `GET /documents/{id}`: retorna os metadados de um documento.
- `POST /search`: recupera trechos semanticamente relevantes, sem usar LLM.
- `POST /chat`: responde a uma pergunta usando apenas os trechos recuperados e retorna as fontes.
- `POST /documents/{id}/reindex`: indexa documentos enviados antes do pipeline vetorial.

Use `http://localhost:8000/docs` para testar os endpoints interativamente.

Após cadastro ou login, copie `access_token`, clique em **Authorize** no Swagger e informe:

```text
Bearer SEU_ACCESS_TOKEN
```

Documentos, busca semântica e chat exigem esse token. A organização é obtida do usuário autenticado no backend; não existe campo `organization_id` aceito pelo frontend.

Exemplo de corpo para `POST /chat`:

```json
{
  "question": "Qual banco de dados é utilizado?"
}
```

Quando não houver contexto relevante, o Noctua não usa conhecimento geral: retorna uma mensagem de insuficiência de informações e uma lista vazia de fontes.
