# Jabuti

API CRUD de usuários com **FastAPI**, pensada para o teste técnico da Jabuti AGI.

## Estado atual (Etapa 1)

- Estrutura de pastas em camadas (`routes` → `services` → `repositories`).
- **Poetry** com dependências de runtime e desenvolvimento.
- **Docker Compose** com PostgreSQL e Redis (apenas infraestrutura local; a app ainda não se conecta a eles).
- Sem aplicação FastAPI, banco, models ou endpoints nesta etapa.

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
```

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
├── api/routes/   # rotas FastAPI
├── core/         # configuração central
├── db/           # sessão e engine (etapas seguintes)
├── models/
├── schemas/
├── repositories/
├── services/
├── cache/
├── exceptions/
└── tests/
```

## Próximos passos

Configuração base da aplicação FastAPI, depois banco async e Alembic (conforme roteiro do projeto).
