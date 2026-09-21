# Handoff do frontend — Noctua

## Objetivo do sistema

O Noctua é uma base de conhecimento com IA. Usuários enviam PDF/TXT, fazem perguntas sobre os documentos de sua organização e recebem respostas fundamentadas com fontes.

## Stack utilizada

- Frontend: React 19, TypeScript, Vite e CSS puro.
- Backend: Python, FastAPI, PostgreSQL, pgvector, OpenAI e Docker.
- Autenticação: JWT emitido pelo backend.

## Estado atual do frontend

Existe uma tela de acesso com modos de login e cadastro. Ela chama `POST /auth/login` ou `POST /auth/register`, guarda `access_token` em `sessionStorage` e alterna para um dashboard inicial.

O dashboard atual é somente estrutural. Upload, listagem de documentos e chat ainda não estão ligados aos endpoints, apesar de o backend já fornecê-los.

## Páginas e componentes implementados

- Tela de acesso: login e cadastro alternáveis no mesmo componente.
- `Dashboard`: cabeçalho Noctua, botão Sair e painel inicial.
- Campo de senha com botão para alternar visibilidade.

Ainda não há roteamento; o estado `autenticado` decide qual tela é exibida.

## Decisões visuais

- Layout dividido: marca à esquerda, acesso à direita.
- Dashboard com fundo claro e cartões.
- Identidade minimalista de coruja por meio do símbolo `◉` ao lado de Noctua.
- Referência visual discreta à Suíça por vermelho e branco.

## Paleta, fontes e imagens

- Vermelho principal: `#d52b1e`.
- Branco: `#ffffff`.
- Fundo claro: `#f8f7f4`.
- Texto escuro: `#242424`.
- Fonte de interface: DM Sans.
- Fonte de títulos: Playfair Display.
- As fontes são carregadas pelo Google Fonts em `src/styles.css`.
- Não há imagens raster; não foi gerado nem adicionado um arquivo de logo de coruja.

## Problemas conhecidos

- O build falha em `src/App.tsx` porque `ImportMeta` não reconhece `env` (`Property 'env' does not exist on type 'ImportMeta'`). É necessário adicionar a declaração de tipos do Vite, normalmente por `src/vite-env.d.ts` com `/// <reference types="vite/client" />`.
- O dashboard ainda não chama `GET /documents`, `POST /documents` ou `POST /chat`.
- Os novos estilos de `.campo-senha` ainda não foram criados.
- A comunicação local precisa da alteração CORS pendente em `docker-compose.yml`/backend ser revisada e validada.

## Arquivos principais

- `noctua_frontend/src/App.tsx`: tela de acesso, autenticação e dashboard inicial.
- `noctua_frontend/src/styles.css`: identidade visual e responsividade.
- `noctua_frontend/src/main.tsx`: ponto de entrada React.
- `noctua_frontend/package.json`: scripts do Vite.
- `noctua_backend/app/main.py`: API FastAPI e configuração CORS pendente.
- `docker-compose.yml`: containers e volume de desenvolvimento do frontend pendente.

## Comandos para executar

Na raiz:

```bash
docker compose up --build
```

Somente o frontend:

```bash
cd noctua_frontend
npm run dev
```

Build do frontend:

```bash
cd noctua_frontend
npm run build
```

## Testes que funcionam

- Backend: `cd noctua_backend && uv run pytest` — última validação conhecida: 16 testes aprovados.
- Frontend: não há testes automatizados configurados.
- Build frontend: está falhando pelo problema de tipo `ImportMeta.env` descrito acima.

## Tarefa em andamento

Conectar e finalizar o dashboard da Sprint 6: carregar documentos da organização, fazer upload autenticado e enviar perguntas ao endpoint `POST /chat`, preservando a identidade visual existente.

## Próximos passos recomendados

1. Corrigir a declaração de tipos do Vite e executar `npm run build`.
2. Criar estilos para o campo de senha, botão de olho e estados de carregamento/sucesso/erro.
3. Conectar o dashboard a `GET /documents` com Bearer token.
4. Conectar upload a `POST /documents` com `FormData`.
5. Conectar chat a `POST /chat`, exibindo resposta e fontes.
6. Validar CORS e hot reload via Docker.
7. Executar build e testes antes de commitar.
