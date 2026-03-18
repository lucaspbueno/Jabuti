# Jabuti

API CRUD de usuários desenvolvida para o teste técnico da Jabuti AGI, com foco em código simples, arquitetura em camadas, tipagem consistente e facilidade de explicação em entrevista técnica.

## Visão geral

O projeto implementa um CRUD de usuários com:

- FastAPI como camada HTTP
- SQLAlchemy 2.0 async e PostgreSQL para persistência
- Redis para cache de leitura
- Alembic preparado para migrations
- arquitetura em camadas com fluxo `routes -> services -> repositories`
- tratamento global de erros com exceptions de domínio
- testes unitários, de serviço, de integração e de cache

## Stack utilizada

| Área | Tecnologia |
| --- | --- |
| API | FastAPI, Uvicorn, Pydantic |
| Persistência | PostgreSQL, SQLAlchemy 2 async, asyncpg, Alembic |
| Cache | Redis |
| Qualidade | Ruff, Mypy, Pytest, pytest-asyncio |
| Ambiente | Poetry, Docker Compose |

## Decisões técnicas principais

- Arquitetura em camadas para separar HTTP, regra de negócio, persistência e cache.
- `UserService` concentra regras de negócio e orquestração.
- `UserRepository` concentra acesso ao banco com `AsyncSession`.
- Rotas finas, sem regra de negócio e sem acesso direto ao banco.
- Exceptions de domínio desacopladas de `HTTPException`, traduzidas por handlers globais.
- Cache integrado na service para manter chaves, serialização e invalidação em um único ponto.
- Soft delete no usuário, com exclusão lógica e ocultação em leituras futuras.

## Arquitetura do projeto

Fluxo principal:

```text
routes -> services -> repositories
```

Responsabilidades:

- `api/routes`: recebe request, valida entrada e delega para a service
- `services`: aplica regras de negócio e coordena persistência + cache
- `repositories`: executa queries e operações de banco
- `cache`: encapsula cliente Redis, serialização JSON e chaves
- `exceptions`: define erros de domínio e handlers globais

## Estrutura de pastas

```text
app/
├── main.py
├── api/
│   ├── deps.py
│   ├── router.py
│   └── routes/
│       ├── health.py
│       └── users.py
├── cache/
│   ├── cache_keys.py
│   ├── cache_service.py
│   └── redis_client.py
├── constants/
├── core/
├── db/
├── exceptions/
├── models/
├── repositories/
├── schemas/
├── services/
└── tests/
    └── integration/
```

## Instalação

Pré-requisitos:

- Python 3.11+
- [Poetry](https://python-poetry.org/docs/#installation)
- Docker e Docker Compose

Passos:

```bash
cd Jabuti
poetry install
cp .env.example .env
```

## Variáveis de ambiente

Exemplo disponível em `.env.example`.

Variáveis principais:

```env
APP_NAME=Jabuti API
ENVIRONMENT=development
DEBUG=false
API_PREFIX=/api/v1

DATABASE_URL=postgresql+asyncpg://jabuti:jabuti@localhost:5432/jabuti
POSTGRES_USER=jabuti
POSTGRES_PASSWORD=jabuti
POSTGRES_DB=jabuti

REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL_SECONDS=300
```

## Executando com Docker Compose

Suba PostgreSQL e Redis:

```bash
docker compose up -d
```

Serviços esperados:

- PostgreSQL em `localhost:5432`
- Redis em `localhost:6379`

## Executando a API

```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Endpoints úteis:

- documentação OpenAPI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- healthcheck: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

## Migrations

O Alembic está configurado e integrado às settings da aplicação.

Com `DATABASE_URL` configurada:

```bash
poetry run alembic revision -m "descricao_da_migration"
poetry run alembic upgrade head
```

Observação:

- a infraestrutura de Alembic está pronta, mas a migration de domínio final não foi gerada como parte deste fluxo incremental

## Endpoints disponíveis

### Healthcheck

- `GET /api/v1/health`

Resposta:

```json
{
  "status": "healthy",
  "app_name": "Jabuti API",
  "environment": "development"
}
```

### Usuários

- `POST /api/v1/users`
- `GET /api/v1/users/{user_id}`
- `GET /api/v1/users?limit=10&offset=0`
- `PUT /api/v1/users/{user_id}`
- `DELETE /api/v1/users/{user_id}`

Contratos:

- `UserCreate`: `name`, `email`, `password`
- `UserUpdate`: `name`, `email`, `password`, `active`
- `UserResponse`: `id`, `name`, `email`, `active`, `created_at`, `updated_at`
- `UserListResponse`: `items`, `total`, `limit`, `offset`

Regras de entrada:

- `email` válido com `EmailStr`
- `password` obrigatória na criação
- `password` nunca aparece em resposta
- listagem com `limit` e `offset`

## Estratégia de cache

O cache foi integrado na `UserService` para manter a feature coesa e evitar espalhar lógica de Redis por rotas ou repositories.

Chaves utilizadas:

- `users:detail:{id}`
- `users:list:{limit}:{offset}`

Leituras com cache:

- `GET /users/{user_id}`
- `GET /users?limit=X&offset=Y`

Invalidação aplicada:

- `create_user` invalida todo cache de listagem
- `update_user` invalida o detalhe do usuário e todo cache de listagem
- `delete_user` invalida o detalhe do usuário e todo cache de listagem

## Tratamento de erros

As services lançam exceptions de domínio e os handlers globais convertem isso em respostas HTTP padronizadas.

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

Casos tratados:

- `UserNotFoundError` -> `404`
- `UserEmailAlreadyExistsError` -> `409`
- erro de validação -> `422`
- erro inesperado -> `500`

## Testes

Rodar toda a suíte:

```bash
poetry run pytest
```

Rodar apenas integração:

```bash
poetry run pytest app/tests/integration
```

Rodar verificações de qualidade:

```bash
poetry run ruff check app alembic
poetry run ruff format --check app alembic
poetry run mypy app alembic
```

A cobertura atual inclui:

- testes unitários de schemas, repository, service e cache
- testes de rotas e handlers
- testes de composição de dependências
- testes de integração da API com PostgreSQL e Redis reais

## Observações e trade-offs

- O projeto prioriza clareza e organização sobre abstrações avançadas.
- O cache foi integrado diretamente na service para manter o fluxo fácil de explicar.
- O controle transacional ficou centralizado nas dependências da API, evitando `commit` no repository.
- O soft delete simplifica exclusão lógica e preserva histórico potencial, sem aumentar muito a complexidade.

## Status de entrega

O projeto está pronto para execução local, revisão técnica e demonstração dos fluxos principais da API.
