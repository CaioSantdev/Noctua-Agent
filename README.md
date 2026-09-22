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
   docker compose up -d --build
   ```

3. Verifique o backend em `http://localhost:8000/health` e o frontend em `http://localhost:5173`. O healthcheck confirma a API e a conexão PostgreSQL.

## Estrutura

- `noctua_backend/`: API FastAPI e testes, com dependências geridas por `uv`.
- `noctua_frontend/`: aplicação React + TypeScript + Vite.
- `docker-compose.yml`: frontend, backend, PostgreSQL com pgvector, Redis e worker Celery.
- `noctua_database/init/`: inicialização da extensão `vector` em bancos novos.

## Escopo atual

As Sprints 0 a 6 estão concluídas e a Sprint 7 está em finalização. O Noctua possui upload e indexação assíncrona de PDF/TXT, busca vetorial multilíngue, chat RAG com fontes, autenticação JWT, isolamento por organização e interface web em React.

O frontend nunca recebe `OPENAI_API_KEY` nem escolhe `organization_id`. O backend obtém a organização pelo usuário autenticado e restringe documentos, chunks, busca e chat a esse tenant.

### Configuração da busca

- Preencha `OPENAI_API_KEY` apenas no `.env` local; nunca a inclua no frontend ou em commits.
- `LIMIAR_SIMILARIDADE=0.30` é o ponto inicial para recuperação multilíngue. Um limiar menor amplia a recuperação e pode trazer trechos menos precisos; ele deverá ser calibrado com documentos reais à medida que a base crescer.

## Endpoints disponíveis

- `GET /health`: confirma a API e o PostgreSQL.
- `POST /auth/register`: cria uma organização e seu primeiro usuário.
- `POST /auth/login`: autentica um usuário e retorna um JWT.
- `POST /documents`: recebe um campo multipart chamado `arquivo` com PDF de até 5 páginas ou TXT, ambos limitados a 10 MB, e responde com status `pending`.
- `GET /documents`: lista os documentos enviados.
- `GET /documents/{id}`: retorna os metadados de um documento.
- `POST /search`: recupera trechos semanticamente relevantes, sem usar LLM.
- `POST /chat`: responde a uma pergunta usando apenas os trechos recuperados e retorna as fontes.
- `POST /documents/{id}/reindex`: enfileira novamente a indexação de um documento.

Use `http://localhost:8000/docs` para testar os endpoints interativamente.

Após cadastro ou login, copie `access_token`, clique em **Authorize** no Swagger e informe:

```text
Bearer SEU_ACCESS_TOKEN
```

Documentos, busca semântica e chat exigem esse token. A organização é obtida do usuário autenticado no backend; não existe campo `organization_id` aceito pelo frontend.

## Interface web

Abra `http://localhost:5173` para acessar a aplicação.

- Login e cadastro compartilham a mesma tela de acesso.
- O dashboard permite enviar PDF/TXT, listar documentos da organização e perguntar ao chat RAG.
- Respostas do chat exibem as fontes retornadas pela API.
- O token é mantido em `sessionStorage` e enviado como Bearer token.

Para desenvolvimento, o container do frontend monta `noctua_frontend/` como volume e atualiza o navegador automaticamente após alterações em `src/`.

## Processamento assíncrono

O envio não aguarda a extração do arquivo, os embeddings ou a OpenAI. A API persiste o
documento e envia seu identificador ao Redis; o worker Celery faz o processamento em
segundo plano.

```text
POST /documents → pending → Redis/Celery → processing → ready | failed
```

O dashboard atualiza a lista automaticamente a cada três segundos enquanto houver
documentos pendentes ou em processamento. Para acompanhar os serviços pelo terminal:

```bash
docker compose logs -f backend worker redis
```

API e worker são executados com o usuário sem privilégios `noctua`. O serviço interno
`permissoes_arquivos` ajusta somente a posse do volume de arquivos durante a inicialização,
inclusive para arquivos persistidos de execuções anteriores.

## Qualidade e robustez

- Senhas usam `scrypt` com salt aleatório; nunca são persistidas em texto puro.
- A OpenAI recebe retry com backoff apenas em falhas transitórias.
- Chave inválida, requisição inválida e saldo esgotado não recebem retry.
- Os testes do backend são executados com:

  ```bash
  cd noctua_backend
  uv run pytest
  ```

- A suíte atual possui 18 testes, incluindo as transições do worker entre `pending`,
  `processing`, `ready` e `failed`.
- O build do frontend pode ser validado com `cd noctua_frontend && npm run build`.

## Deploy

Antes de publicar, configure no provedor escolhido as variáveis `DATABASE_URL`,
`REDIS_URL`, `JWT_SECRET`, `OPENAI_API_KEY`, `DIRETORIO_ARQUIVOS` e a origem permitida
no CORS. PostgreSQL, Redis e os arquivos enviados devem usar armazenamento persistente.
Nunca copie o arquivo `.env` local para o repositório ou para o frontend.

## Próximas evoluções

- Memória de conversa.
- Visualização ou download protegido dos arquivos originais pelas fontes do chat.

Exemplo de corpo para `POST /chat`:

```json
{
  "question": "Qual banco de dados é utilizado?"
}
```

Quando não houver contexto relevante, o Noctua não usa conhecimento geral: retorna uma mensagem de insuficiência de informações e uma lista vazia de fontes.
