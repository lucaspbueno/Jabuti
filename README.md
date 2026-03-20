# Jabuti - Desafio Técnico (API CRUD de Usuários)

API desenvolvida com **Python + FastAPI** usando arquitetura em camadas (`routes -> services -> repositories`), persistência com **PostgreSQL** (SQLAlchemy async + Alembic) e cache com **Redis**.

> Execução do projeto **exclusivamente com Docker**.

## Como rodar (Docker)

### 1) Configurar variáveis de ambiente

```bash
cp .env.example .env
```

### 2) Subir toda a stack

```bash
docker compose up --build
```

### 3) Acessar a aplicação

- API: [http://localhost:8000](http://localhost:8000)
- Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
- OpenAPI JSON: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

### 4) Parar os containers

```bash
docker compose down
```

### Observações importantes

- O container da API executa `alembic upgrade head` no startup.
- A API roda com hot reload habilitado (`uvicorn --reload`) para refletir alterações de código em tempo real no ambiente Docker.
- O diretório `./app` do host é montado em `/app` no serviço `api` (`docker-compose.yml`), para que mudanças locais cheguem ao processo dentro do container.
- Serviços no `docker-compose.yml`:
  - `api` (porta `8000`)
  - `postgres` (porta `5432`)
  - `redis` (porta `6379`)

## Sumário

- [Tecnologias](#tecnologias)
- [Arquitetura](#arquitetura)
- [Estrutura de pastas](#estrutura-de-pastas)
- [Variáveis de ambiente](#variáveis-de-ambiente)
- [Endpoints](#endpoints)
- [Cache](#cache)
- [Tratamento de erros](#tratamento-de-erros)
- [Testes](#testes)

## Tecnologias

- Python 3.11
- FastAPI
- SQLAlchemy 2.0 (async) + asyncpg
- PostgreSQL
- Redis
- Alembic
- Pydantic / pydantic-settings
- Poetry
- Ruff
- Mypy
- Pytest / pytest-asyncio
- Docker / Docker Compose

## Arquitetura

O projeto segue separação clara de responsabilidades:

- `routes`: recebe request/response HTTP e valida parâmetros de entrada.
- `services`: concentra regras de negócio.
- `repositories`: encapsula acesso ao banco.

A aplicação também inclui:

- camada de cache Redis reutilizável;
- exceções de domínio + handlers globais;
- injeção de dependências via FastAPI (`Depends`);
- composição de infraestrutura no `app.state` (`db`, `redis`, `settings`).

## Estrutura de pastas

```text
app/
├── api/
│   ├── dependencies/
│   ├── routes/
│   └── router.py
├── cache/
├── constants/
├── core/
├── db/
├── exceptions/
├── interfaces/
├── models/
├── repositories/
├── schemas/
├── security/
├── services/
├── tests/
└── main.py
```

## Variáveis de ambiente

Principais variáveis (arquivo `.env`):

- `APP_NAME`
- `ENVIRONMENT`
- `DEBUG`
- `API_PREFIX` (padrão: `/api/v1`)
- `DATABASE_URL`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `REDIS_URL`
- `REDIS_CACHE_TTL_SECONDS`

Use `.env.example` como base.

## Endpoints

Prefixo padrão: `API_PREFIX=/api/v1`.

### Usuários

- `POST /api/v1/users` - criar usuário
- `GET /api/v1/users?limit=10&offset=0` - listar usuários com paginação
- `GET /api/v1/users/{user_id}` - buscar usuário por ID
- `PUT /api/v1/users/{user_id}` - atualizar usuário
- `DELETE /api/v1/users/{user_id}` - remover usuário (soft delete)

Em `{user_id}` use um **UUID** válido (ex.: `550e8400-e29b-41d4-a716-446655440000`). O texto literal `user_id` não é aceito e resulta em **422**.

Exemplos com `curl` (substitua o UUID pelo retornado no `POST` ou por um existente no banco):

```bash
# Criar usuário (JSON obrigatório: name, email, password)
curl -sS -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{"name":"Maria","email":"maria@example.com","password":"senha-segura"}'

# Listar com paginação
curl -sS "http://localhost:8000/api/v1/users?limit=10&offset=0"

# Buscar por ID
curl -sS "http://localhost:8000/api/v1/users/550e8400-e29b-41d4-a716-446655440000"
```

Para ver **detalhes** de erros de validação (422) no corpo da resposta, use `DEBUG=true` no `.env` (campo `error.details`).

**Nota (FastAPI + `Depends`):** a composição de serviços (`get_user_service`, `get_cache_service`, etc.) fica em **funções no módulo** `app/api/dependencies/`. Usar `@staticmethod` com parâmetros `Depends(...)` faz o FastAPI tratar esses nomes como **query obrigatória** e devolver 422 em todas as rotas — não use esse padrão.

### Contratos principais

- `UserCreate`: `name`, `email`, `password`
- `UserUpdate`: atualização parcial de `name`, `email`, `password`, `active`
- `UserResponse`: resposta pública sem campo `password`
- `UserListResponse`: `items`, `total`, `limit`, `offset`

## Cache

A camada de cache usa Redis para otimizar leituras:

- detalhe: `users:detail:{id}`
- listagem: `users:list:{limit}:{offset}`

Invalidação aplicada em operações de escrita:

- criação: invalida cache de listagens;
- atualização: invalida detalhe + listagens;
- remoção: invalida detalhe + listagens.

## Tratamento de erros

Padrão com exceções de domínio (`AppError`) e handlers globais:

- `404` para recurso não encontrado;
- `409` para conflito de negócio (ex.: email já existente);
- `422` para validação;
- `500` para erro inesperado.

Formato padrão de erro:

```json
{
  "error": {
    "code": "user_not_found",
    "message": "Usuário com id '...' não encontrado.",
    "details": null
  }
}
```

## Testes

A suíte está em `app/tests` com cobertura de:

- schemas;
- repositories;
- services;
- rotas;
- dependências;
- cache;
- handlers de exceção.

Exemplo para executar testes dentro do container da API:

```bash
docker compose run --rm api poetry run pytest
```
