# Jabuti

API CRUD de usuários com **FastAPI**, pensada para o teste técnico da Jabuti AGI.

## Estado atual (Etapa 12)

- Aplicação **FastAPI** com ponto de entrada `app.main:app` e factory `create_app()`.
- **Settings** centralizados (`pydantic-settings`): `.env` + variáveis de ambiente; `DATABASE_URL` já utilizada para engine async e Alembic.
- Endpoint **`GET {API_PREFIX}/health`** (padrão `/api/v1/health`) com resposta JSON (`status`, `app_name`, `environment`).
- Camadas: schema `HealthStatusResponse` → `SystemHealthService` → rota (sem banco, Redis ou CRUD).
- Arquivo **`.env.example`** na raiz do projeto.
- Infra de persistência configurada: **SQLAlchemy 2 async** (`Base`), engine e sessão async, integração com **Alembic**.
- Gerenciador de sessão do banco mantido em POO, com contexto assíncrono para abrir/fechar sessões por requisição sem expor iteração no consumo.
- Model de domínio **`User`** definido em `app.models.user` (tabela `user`, colunas próprias + herança de campos comuns da `Base`).
- Schemas Pydantic da feature de usuário implementados em `app.schemas.user`: criação, atualização parcial e resposta pública.
- Restrições compartilhadas da feature de usuário centralizadas em `app.constants.user`, evitando duplicação entre ORM e Pydantic.
- Camada de persistência da feature implementada em `app.repositories.user_repository.UserRepository`.
- Camada de negócio da feature implementada em `app.services.user_service.UserService`, com validação de unicidade de email e tratamento de usuário inexistente.
- Tratamento global de erros implementado com exceptions de domínio e handlers padronizados no FastAPI.
- Endpoints CRUD da feature de usuário implementados com FastAPI, usando `UserService` por injeção de dependência.
- Dependências de banco separadas entre leitura e escrita: rotas `GET` não fazem `commit`, enquanto mutações mantêm `commit/rollback` centralizados.
- Testes de dependências da API cobrem os fluxos de sessão de leitura e escrita, incluindo `rollback` em erro.
- Camada reutilizável de cache com Redis implementada em POO, com cliente async, serviço de cache JSON e padronização centralizada de chaves.
- Cache Redis integrado à feature de usuários para detalhe e listagem, com invalidação consistente nas operações de escrita.
- Cobertura automatizada atual focada em testes unitários e de serviço, validando regras da API e comportamento de cache sem exigir banco e Redis dedicados para teste.

*(Etapas anteriores: Poetry, estrutura de pastas, Docker Compose, smoke de dependências, healthcheck.)*

## Stack

| Área        | Tecnologia                          |
| ----------- | ----------------------------------- |
| API         | FastAPI, Uvicorn, Pydantic          |
| Banco       | PostgreSQL, SQLAlchemy 2 async, asyncpg, Alembic |
| Cache       | Redis                               |
| Qualidade   | Ruff, Mypy, Pytest, pytest-asyncio  |
| Ambiente    | Poetry, Docker Compose              |

## Pré-requisitos

- Python 3.11+
- [Poetry](https://python-poetry.org/docs/#installation)
- Docker e Docker Compose (opcional, para subir Postgres e Redis)

## Instalação

```bash
cd Jabuti
poetry install
cp .env.example .env   # opcional; ajuste variáveis
```

## Executar a API

```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Documentação interativa: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Healthcheck: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health) (se `API_PREFIX` for o padrão)

## Infraestrutura local (Postgres + Redis)

```bash
docker compose up -d
```

Credenciais padrão do Postgres no compose: usuário `jabuti`, senha `jabuti`, banco `jabuti`, porta `5432`. Redis na porta `6379`.

## Qualidade e testes

```bash
poetry run ruff check app alembic
poetry run ruff format --check app alembic
poetry run mypy app alembic
poetry run pytest
```

A suíte atual de testes não exige banco nem Redis dedicados. Os cenários de cache e regras de negócio cobertos hoje usam mocks nos testes de serviço.

## Estrutura do pacote `app`

```
app/
├── main.py           # FastAPI / Application
├── api/
│   ├── deps.py       # composição de session/repository/service
│   ├── router.py
│   └── routes/       # health, users
├── core/             # Settings
├── constants/        # constantes compartilhadas por feature
├── db/               # Base ORM + engine/sessão async
├── models/           # ex.: User
├── schemas/          # health e contratos de usuário
├── repositories/     # ex.: UserRepository
├── services/         # health e UserService
├── cache/            # cliente Redis, serviço e chaves de cache
├── exceptions/       # domínio + handlers globais
└── tests/            # testes unitários, de serviço e de composição da aplicação
```

## Migrations (Alembic)

Com o `.env` configurado (incluindo `DATABASE_URL`):

```bash
poetry run alembic revision -m "criar tabela X"
poetry run alembic upgrade head
```

Nesta etapa ainda **não** há migrations de negócio aplicadas; o Alembic está preparado para enxergar os models quando elas forem criadas.

## Contratos de usuário

- `UserCreate`: `name`, `email`, `password`
- `UserUpdate`: atualização parcial de `name`, `email`, `password` e `active`
- `UserResponse`: `id`, `name`, `email`, `active`, `created_at`, `updated_at`
- `UserListResponse`: `items`, `total`, `limit`, `offset`

Validações já implementadas:

- `email` válido com `EmailStr`
- `password` obrigatória na criação e com tamanho mínimo
- `UserUpdate` exige pelo menos um campo informado
- `password` não aparece em schemas de saída
- limites compartilhados de `User` centralizados em um único módulo reutilizado por `model` e `schemas`

## Repository de usuário

`UserRepository` concentra apenas acesso a dados com `AsyncSession`, sem regra de negócio e sem acoplamento ao FastAPI.

Operações disponíveis:

- `get_by_id`
- `get_by_email`
- `list_users(limit, offset)`
- `count()`
- `create(...)`
- `update(...)`
- `delete(...)`

Nesta etapa o repository usa `flush` e `refresh`, mas não faz `commit`; o controle transacional fica centralizado nas dependências de escrita.

## Service de usuário

`UserService` centraliza regras de negócio e orquestra o fluxo entre schemas e `UserRepository`, sem acesso direto ao banco e sem acoplamento ao FastAPI.

Regras implementadas:

- usuário precisa existir para busca individual, atualização e exclusão
- não é permitido criar usuário com email já existente
- não é permitido atualizar email para um valor já usado por outro usuário
- respostas públicas continuam sem expor `password`
- usuários excluídos logicamente deixam de aparecer nas consultas do repository

## Endpoints de usuário

Rotas disponíveis:

- `POST /api/v1/users`
- `GET /api/v1/users/{user_id}`
- `GET /api/v1/users?limit=10&offset=0`
- `PUT /api/v1/users/{user_id}`
- `DELETE /api/v1/users/{user_id}`

Decisões desta etapa:

- rotas finas, sem regra de negócio
- composição via dependências: `AsyncSession` -> `UserRepository` -> `UserService`
- rotas de leitura usam sessão sem `commit` automático; rotas de escrita usam sessão transacional com `commit/rollback`
- `limit` e `offset` em query params, com validação simples no FastAPI
- listagem retorna envelope paginado simples com `items`, `total`, `limit` e `offset`
- `password` nunca aparece nas respostas
- erros de domínio seguem sendo traduzidos pelos handlers globais

## Camada de cache

Componentes implementados:

- `redis_client.py`: cliente Redis async reutilizável
- `cache_service.py`: leitura, escrita e remoção de dados JSON com TTL
- `cache_keys.py`: geração padronizada de chaves da aplicação

Configurações disponíveis:

- `REDIS_URL`
- `REDIS_CACHE_TTL_SECONDS`

Padrões de chave já definidos:

- `users:detail:{id}`
- `users:list:{limit}:{offset}`

Operações disponíveis na camada de cache:

- `get_json(key)`
- `set_json(key, value, ttl_seconds=None)`
- `delete(key)`
- `delete_by_prefix(prefix)`

Contrato atual do cache JSON:

- o `CacheService` salva e lê sempre um objeto JSON (`dict`)
- os endpoints de listagem usam `UserListResponse` como envelope serializado
- isso evita ambiguidade entre `dict` e `list` e simplifica a tipagem da camada

## Integração do cache na feature de usuários

O cache foi integrado na `UserService`, mantendo:

- rotas finas
- repository focado em banco
- chaves, serialização e invalidação concentradas em um único ponto de orquestração
- `CacheService` como dependência obrigatória do `UserService`, sem fallback nulo dentro da regra de negócio

Leituras com cache:

- `GET /users/{user_id}` usa `users:detail:{id}`
- `GET /users?limit=X&offset=Y` usa `users:list:{limit}:{offset}`

Estratégia de invalidação:

- `create_user` -> invalida todo cache de listagem
- `update_user` -> invalida detalhe do usuário + todo cache de listagem
- `delete_user` -> invalida detalhe do usuário + todo cache de listagem

Decisão de contrato desta etapa:

- o `UserService` sempre recebe `UserRepository` e `CacheService`
- testes unitários do service também injetam mock de cache para refletir o mesmo contrato da aplicação

## Cobertura de testes atual

A cobertura automatizada atual prioriza cenários que podem ser validados sem infraestrutura dedicada:

- testes de service para CRUD de usuários e regras de negócio
- testes de cache na `UserService` com mocks para leitura, preenchimento e invalidação
- testes de rotas, handlers, dependências e smoke tests da aplicação

## Tratamento de erros

As regras de negócio continuam lançando exceções de domínio, sem acoplamento com `HTTPException`.

Estratégia adotada:

- `AppError` como base para erros padronizados da aplicação
- exceptions da feature de usuário herdando dessa base
- handlers globais registrados na criação do `FastAPI`
- respostas JSON padronizadas para erros de domínio, validação e falhas inesperadas

Formato padrão:

```json
{
  "error": {
    "code": "user_not_found",
    "message": "Usuário com id '...' não encontrado.",
    "details": null
  }
}
```

Casos já cobertos:

- `UserNotFoundError` -> `404`
- `UserEmailAlreadyExistsError` -> `409`
- erro de validação -> `422`
- erro HTTP do framework -> status original com envelope padronizado
- erro inesperado -> `500`

## Próximos passos

Ajustes finais, revisão do projeto e README de entrega.
