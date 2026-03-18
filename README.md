# Jabuti

API CRUD de usuários com **FastAPI**, pensada para o teste técnico da Jabuti AGI.

## Estado atual (Etapa 8)

- Aplicação **FastAPI** com ponto de entrada `app.main:app` e factory `create_app()`.
- **Settings** centralizados (`pydantic-settings`): `.env` + variáveis de ambiente; `DATABASE_URL` já utilizada para engine async e Alembic.
- Endpoint **`GET {API_PREFIX}/health`** (padrão `/api/v1/health`) com resposta JSON (`status`, `app_name`, `environment`).
- Camadas: schema `HealthStatusResponse` → `SystemHealthService` → rota (sem banco, Redis ou CRUD).
- Arquivo **`.env.example`** na raiz do projeto.
- Infra de persistência configurada: **SQLAlchemy 2 async** (`Base`), engine e sessão async, integração com **Alembic**.
- Model de domínio **`User`** definido em `app.models.user` (tabela `user`, colunas próprias + herança de campos comuns da `Base`).
- Schemas Pydantic da feature de usuário implementados em `app.schemas.user`: criação, atualização parcial e resposta pública.
- Restrições compartilhadas da feature de usuário centralizadas em `app.constants.user`, evitando duplicação entre ORM e Pydantic.
- Camada de persistência da feature implementada em `app.repositories.user_repository.UserRepository`.
- Camada de negócio da feature implementada em `app.services.user_service.UserService`, com validação de unicidade de email e tratamento de usuário inexistente.
- Tratamento global de erros implementado com exceptions de domínio e handlers padronizados no FastAPI.

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

## Estrutura do pacote `app`

```
app/
├── main.py           # FastAPI / Application
├── api/
│   ├── deps.py       # dependências das rotas
│   ├── router.py
│   └── routes/       # health, ...
├── core/             # Settings
├── constants/        # constantes compartilhadas por feature
├── db/               # Base ORM + engine/sessão async
├── models/           # ex.: User
├── schemas/          # health e contratos de usuário
├── repositories/     # ex.: UserRepository
├── services/         # health e UserService
├── cache/
├── exceptions/       # domínio + handlers globais
└── tests/
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

Nesta etapa o repository usa `flush` e `refresh`, mas não faz `commit`; o controle transacional ficará para a camada superior.

## Service de usuário

`UserService` centraliza regras de negócio e orquestra o fluxo entre schemas e `UserRepository`, sem acesso direto ao banco e sem acoplamento ao FastAPI.

Regras implementadas:

- usuário precisa existir para busca individual, atualização e exclusão
- não é permitido criar usuário com email já existente
- não é permitido atualizar email para um valor já usado por outro usuário
- respostas públicas continuam sem expor `password`
- usuários excluídos logicamente deixam de aparecer nas consultas do repository

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

Endpoints CRUD da feature de usuário consumindo `UserService` e os handlers globais.
