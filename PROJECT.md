# Noctua

## Estado atual

Sprint 6 concluída no frontend. Sprint 7 em andamento: processamento assíncrono de
documentos com Redis e Celery.

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
- Esta sprint foi concluída antes da autenticação; atualmente os documentos pertencem à organização do usuário autenticado.

## Sprint 2 - Busca vetorial

- A organização padrão foi usada somente na etapa inicial de desenvolvimento; atualmente o tenant é obtido do JWT e do usuário persistido.
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

## Sprint 4 - Autenticação e multi-tenancy

- Entidades `Usuario` e `Organizacao` utilizadas para identificar o tenant real.
- Cadastro em `POST /auth/register` cria organização e primeiro usuário; `POST /auth/login` emite JWT.
- Senhas são derivadas com `scrypt`, salt aleatório e comparação em tempo constante; nunca são armazenadas em texto puro.
- JWT é assinado com `JWT_SECRET`, configurada somente no ambiente do backend.
- Upload, listagem, consulta, reindexação, busca vetorial e chat exigem Bearer token.
- O tenant é obtido pelo usuário persistido no backend, e não por `organization_id` enviado pelo cliente.
- Teste automatizado comprova que tenant A não lista nem acessa documento do tenant B.

## Sprint 5 - Qualidade e robustez

- Retry com backoff exponencial implementado para timeout, falha de conexão, 429 transitório e erros internos da OpenAI.
- Falhas permanentes, como credencial inválida, requisição inválida e saldo esgotado, não recebem retry.
- Rotas de busca e chat retornam respostas HTTP seguras e específicas para falhas da IA.
- Testes com mocks validam retry de conexão e ausência de retry para saldo esgotado.

## Preparação de deploy

- A aplicação pode usar PostgreSQL e Storage privados do Supabase por variáveis
  de ambiente, preservando o armazenamento local como padrão de desenvolvimento.
- O guia de deploy orienta o uso do Session pooler do Supabase para ambientes
  IPv4, como Docker local e provedores de nuvem.

## Ainda não implementado

- Finalizar a validação integrada do worker Celery com Redis e PostgreSQL em Docker.
- Deploy em nuvem da aplicação e documentação da infraestrutura escolhida.

## Sprint 7 - Processamento assíncrono

- Criada a branch `feature/sprint-7-processamento-assincrono`.
- Redis foi incluído como broker e backend de resultados do Celery.
- O Compose agora declara os serviços `redis` e `worker`, além de um volume persistente
  para os dados do Redis.
- Upload e reindexação persistem o documento como `pending` e enfileiram o identificador;
  a API não aguarda extração, chunking ou embeddings.
- O worker processa o arquivo compartilhado, transita por `processing` e conclui em
  `ready` ou `failed`.
- Testes automatizados simulam o worker e validam as transições
  `pending → processing → ready` e `pending → processing → failed`.
- O dashboard consulta novamente a lista de documentos a cada três segundos apenas
  enquanto houver itens `pending` ou `processing`; a atualização não substitui a lista
  por uma tela de carregamento.
- API e worker usam o usuário sem privilégios `noctua`; o serviço de inicialização
  `permissoes_arquivos` prepara a posse do volume persistente antes dos dois serviços.

## Deploy - Railway, Supabase e Vercel

- A branch `feature/deploy-railway` prepara o deploy de demonstração.
- Supabase Storage substitui o compartilhamento de diretório local entre API e worker
  em produção; a chave `service_role` permanece exclusiva do backend.
- URLs PostgreSQL genéricas são normalizadas para o driver `psycopg` usado pela API.
- A migration de trechos habilita `vector` antes de criar a coluna de embeddings em
  bancos novos.
- CORS é configurável por `ORIGENS_CORS`, e o frontend possui rewrite Vercel para as
  rotas SPA.
- As fontes do chat informam documento, página e uma prévia limitada do chunk enviado
  como contexto para a LLM; a prévia possui até 220 caracteres.

## Sprint 6 - Interface web

- Tipos de ambiente do Vite declarados em `src/vite-env.d.ts`.
- Acesso e cadastro exibem estados de carregamento, sucesso e erro; a senha pode ser mostrada ou ocultada.
- As telas usam as URLs `/login`, `/cadastro` e `/dashboard`; o dashboard é protegido pela presença do JWT local.
- O dashboard usa o JWT mantido em `sessionStorage` como Bearer token para listar e enviar documentos e para consultar o chat.
- Respostas do chat apresentam suas fontes; respostas 401 encerram a sessão local.
- O painel central alterna entre envio e chat, incluindo as ilustrações correspondentes em `public/imagens`.
- O frontend é organizado em páginas, componentes reutilizáveis, tipos compartilhados e serviço de comunicação com a API.
- Cartões de documentos preservam nomes longos dentro do contorno e distinguem arquivos TXT em azul.
- Estilos do frontend são separados por escopo em `src/styles`, com regras globais, variáveis, login, dashboard, cabeçalho e cartões de documentos.
