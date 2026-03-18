# Jabuti

API CRUD de usuários com **FastAPI**, pensada para o teste técnico da Jabuti AGI.

## Estado atual (Etapa 2)

- Aplicação **FastAPI** com ponto de entrada `app.main:app` e factory `create_app()`.
- **Settings** centralizados (`pydantic-settings`): `.env` + variáveis de ambiente; campos opcionais `DATABASE_URL` e `REDIS_URL` para etapas futuras.
- Endpoint **`GET {API_PREFIX}/health`** (padrão `/api/v1/health`) com resposta JSON (`status`, `app_name`, `environment`).
- Camadas: schema `HealthStatusResponse` → `SystemHealthService` → rota (sem banco, Redis ou CRUD).
- Arquivo **`.env.example`** na raiz do projeto.

*(Etapa 1: Poetry, pastas, Docker Compose, smoke de dependências — mantidos.)*

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
poetry run ruff check app
poetry run ruff format --check app
poetry run mypy app
poetry run pytest
```

## Estrutura do pacote `app`

```
app/
├── main.py           # FastAPI / Application
├── api/
│   ├── deps.py       # dependências das rotas
│   ├── router.py
│   └── routes/       # health, ...
├── core/             # Settings
├── db/               # (etapas seguintes)
├── models/
├── schemas/
├── repositories/
├── services/         # ex.: SystemHealthService
├── cache/
├── exceptions/
└── tests/
```

## Próximos passos

Banco async, Alembic e sessão SQLAlchemy (Etapa 3).
