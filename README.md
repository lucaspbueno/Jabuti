# Jabuti - Desafio Técnico (API CRUD de Usuários)

API desenvolvida com **Python + FastAPI** usando arquitetura em camadas (`routes -> services -> repositories`), persistência com **PostgreSQL** (SQLAlchemy async + Alembic) e cache com **Redis**.

> Execução do projeto **exclusivamente com Docker**.

## Tecnologias

![REST API](https://img.shields.io/badge/api%20rest-02569B?style=for-the-badge&logo=fastapi&logoColor=white) ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![FastAPI](https://img.shields.io/badge/fastapi-009688?style=for-the-badge&logo=fastapi&logoColor=white) ![Docker](https://img.shields.io/badge/docker-0db7ed?style=for-the-badge&logo=docker&logoColor=white) ![Docker Compose](https://img.shields.io/badge/docker%20compose-384d54?style=for-the-badge&logo=docker&logoColor=white) ![Redis](https://img.shields.io/badge/redis-DD0031?style=for-the-badge&logo=redis&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/postgresql-316192?style=for-the-badge&logo=postgresql&logoColor=white) ![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-CC2927?style=for-the-badge&logo=sqlalchemy&logoColor=white) ![Alembic](https://img.shields.io/badge/alembic-000000?style=for-the-badge&logo=alembic&logoColor=white) ![Pytest](https://img.shields.io/badge/pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![Pydantic](https://img.shields.io/badge/pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white) ![Poetry](https://img.shields.io/badge/poetry-60A5FA?style=for-the-badge&logo=poetry&logoColor=white) ![Ruff](https://img.shields.io/badge/ruff-000000?style=for-the-badge&logo=ruff&logoColor=white) ![Mypy](https://img.shields.io/badge/mypy-2A6DB2?style=for-the-badge&logo=python&logoColor=white) ![Uvicorn](https://img.shields.io/badge/uvicorn-499848?style=for-the-badge&logo=python&logoColor=white) ![Swagger](https://img.shields.io/badge/swagger-85EA2D?style=for-the-badge&logo=swagger&logoColor=black) ![ReDoc](https://img.shields.io/badge/redoc-EF3B2D?style=for-the-badge&logo=redoc&logoColor=white) ![Postman](https://img.shields.io/badge/postman-FF6C37?style=for-the-badge&logo=postman&logoColor=white) ![Insomnia](https://img.shields.io/badge/insomnia-4000BF?style=for-the-badge&logo=insomnia&logoColor=white) 

## Como rodar

### 1) Configurar variáveis de ambiente

```bash
cp .env.example .env
```

### 2) Subir toda a stack

```bash
docker compose up -d --build
```

### 3) Acessar a aplicação

- API: [http://localhost:8000](http://localhost:8000)
- Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc	](http://localhost:8000/redoc	)

### 4) Parar os containers

```bash
docker compose down -v --remove-orphans
```

## Sumário

- [Tecnologias](#tecnologias)
- [Get Started](#como-rodar)
- [Arquitetura](#arquitetura)
- [Estrutura de pastas](#estrutura-de-pastas)
- [Variáveis de ambiente](#variáveis-de-ambiente)
- [Collection (Postman e Insomnia)](#collection-postman-e-insomnia)
- [Endpoints](#endpoints)
- [Cache](#cache)
- [Tratamento de erros](#tratamento-de-erros)
- [Testes](#testes)

## Arquitetura

O projeto segue separação clara de responsabilidades:

- `routes`: recebe request/response HTTP e valida parâmetros de entrada com pydantic.
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

## Collection (Postman e Insomnia)

O projeto inclui uma **collection HTTP** em [`postman/Jabuti.collection.json`](postman/Jabuti.collection.json) para testar a API de ponta a ponta.

- **Postman**: importe o arquivo pela opção *Import* (coleção no formato Postman Collection v2.1).
- **Insomnia**: use *Import* → *Choose file* → e selecione o mesmo JSON (funciona tanto para o Postman quanto para o Insomnia).

Por padrão a collection usa `base_url` = `http://localhost:8000` e `api_prefix` = `/api/v1`; altere essas variáveis na collection se o ambiente ou o prefixo da API forem diferentes.

## Endpoints

Host: `https://localhost`
Prefixo padrão: `API_PREFIX=/api/v1`.

### Usuários

- `POST /api/v1/users` - criar usuário
- `GET /api/v1/users?limit=10&offset=0` - listar usuários com paginação
- `GET /api/v1/users/{user_id}` - buscar usuário por ID
- `PATCH /api/v1/users/{user_id}` - atualizar usuário (parcial)
- `DELETE /api/v1/users/{user_id}` - remover usuário (soft delete)

| Método | Endpoint                                      | Descrição                         |
| ------ | --------------------------------------------- | --------------------------------- |
| POST   | `/api/v1/users`                               | Criar usuário                     |
| GET    | `/api/v1/users?limit=10&offset=0`             | Listar usuários com paginação     |
| GET    | `/api/v1/users/{user_id}`                     | Buscar usuário por ID             |
| PATCH  | `/api/v1/users/{user_id}`                     | Atualizar usuário (parcial)       |
| DELETE | `/api/v1/users/{user_id}`                     | Remover usuário (soft delete)     |

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

Para ver **detalhes** de erros de validação no corpo da resposta, use `DEBUG=true` no `.env` (campo `error.details`).

## Testes

A suíte está em `app/tests` com cobertura de:

- schemas;
- repositories;
- services;
- rotas;
- dependências;
- cache;
- handlers de exceção.

### Rodar os testes do zero (com Docker)

- Não é obrigatório subir Postgres/Redis só para estes testes: a suíte atual usa principalmente mocks e não exige banco ou Redis reais ligados.
- O comando abaixo usa o script **`/entrypoint-test.sh`**, que instala o grupo de dependências `dev` e chama o pytest, **sem** subir os outros serviços (`--no-deps`):

```bash
docker compose run --rm --no-deps --entrypoint /entrypoint-test.sh api
```

Se você omitir `--no-deps`, o Compose ainda sobe Postgres e Redis por causa do `depends_on` do serviço `api`, útil só se no futuro existirem testes de integração com esses serviços; para a suíte de hoje isso é desnecessário.

Na primeira execução o `poetry install --with dev` pode demorar um pouco; nas seguintes costuma ser mais rápido. Os logs dessa etapa de instalação de dependências estão omitidos pelo comando `-q` no arquivo **`/entrypoint-test.sh`**.

### Remover a network criada pelo docker-compose após a execução dos testes (Opcional)

```bash
docker network rm jabuti-network
```

---
