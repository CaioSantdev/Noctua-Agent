# Deploy do Noctua: Supabase, Railway e Vercel

Este guia publica o Noctua sem expor segredos no frontend.

## Arquitetura

```text
Vercel (React/Vite)
        ↓
Railway (FastAPI) ── Railway (Redis) ── Railway (Celery Worker)
        ↓                       ↓
Supabase (PostgreSQL + pgvector e Storage privado)
```

## 1. Criar o projeto no Supabase

1. Crie um projeto gratuito.
2. Em **Storage**, crie um bucket privado chamado `documentos`.
3. Em **Settings > API**, copie `Project URL` e a chave `service_role`.
4. Em **Connect**, copie a URL de conexão PostgreSQL.

Não use a chave `service_role` no Vercel ou no frontend. O backend executa as migrations
automaticamente e habilita a extensão `vector` em bancos novos.

## 2. Criar os serviços na Railway

Crie um projeto e adicione um banco **Redis** pelo menu **New > Database**.

Depois crie dois serviços a partir do repositório GitHub e da branch
`feature/deploy-railway`:

| Serviço | Root Directory | Comando de início | Domínio público |
| --- | --- | --- | --- |
| `backend` | `noctua_backend` | Dockerfile padrão | Sim |
| `worker` | `noctua_backend` | `uv run --no-sync celery -A app.infrastructure.celery.aplicacao_celery worker --loglevel=INFO --concurrency=1` | Não |

Configure as variáveis abaixo em **backend** e **worker**. Troque o prefixo da URL do
Supabase de `postgresql://` para `postgresql+psycopg://` antes de cadastrá-la.

```text
DATABASE_URL=postgresql+psycopg://...
REDIS_URL=${{Redis.REDIS_URL}}
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_SERVICE_ROLE_KEY=...
SUPABASE_BUCKET_DOCUMENTOS=documentos
OPENAI_API_KEY=...
JWT_SECRET=...
EXPIRACAO_TOKEN_MINUTOS=60
DIRETORIO_ARQUIVOS=/tmp/noctua-arquivos
MAX_PAGINAS_PDF=5
LIMIAR_SIMILARIDADE=0.30
MAX_TRECHOS_RECUPERADOS=5
MAX_TOKENS_CONTEXTO=4000
MAX_TOKENS_RESPOSTA=500
MODELO_EMBEDDING=text-embedding-3-small
MODELO_LLM=gpt-4.1-mini
```

No `backend`, defina inicialmente `ORIGENS_CORS=http://localhost:5173`. Gere o domínio
público Railway e valide `https://SEU_BACKEND.up.railway.app/health`.

## 3. Publicar o frontend na Vercel

1. Importe o mesmo repositório GitHub e selecione a branch `feature/deploy-railway`.
2. Defina `noctua_frontend` como **Root Directory**.
3. Configure a variável de ambiente de build:

   ```text
   VITE_API_URL=https://SEU_BACKEND.up.railway.app
   ```

4. Faça o deploy. O arquivo `vercel.json` garante que `/login`, `/cadastro` e
   `/dashboard` sejam servidos pelo React mesmo quando acessados diretamente.

Copie o domínio `.vercel.app` gerado e atualize no backend da Railway:

```text
ORIGENS_CORS=https://SEU_FRONTEND.vercel.app
```

Em seguida, redeploy o backend e o frontend.

## 4. Validação final

1. Acesse o frontend Vercel e cadastre uma conta.
2. Envie um TXT pequeno e acompanhe `pending`, `processing` e `ready`.
3. Faça uma pergunta no chat e confirme a fonte retornada.
4. Consulte os logs do backend e worker pela Railway.

Ao terminar a análise, remova os serviços Railway ou deixe o projeto parar para evitar
consumo do crédito de trial.
