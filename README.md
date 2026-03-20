# Jabuti - Desafio Técnico Backend

API REST para CRUD de usuários construída com **FastAPI**, **PostgreSQL**, **Redis** e **Docker Compose**. O projeto foi estruturado em camadas, com suporte a migrations via **Alembic**, cache em Redis para consultas de usuários e documentação automática via OpenAPI/Swagger.

## Como rodar com Docker

> Este projeto deve ser executado **exclusivamente com Docker**.

### 1) Configure as variáveis de ambiente

Na raiz do repositório, crie o arquivo `.env` a partir do exemplo:

```bash
cp .env.example .env
```

Se quiser, ajuste os valores antes de subir os containers. Os defaults já funcionam para o ambiente local com Docker Compose.

### 2) Suba toda a stack

```bash
docker compose up --build
```

Esse comando sobe:

- **PostgreSQL**
- **Redis**
- **API FastAPI**

Durante a inicialização da API, o container executa automaticamente:

- `alembic upgrade head`
- `uvicorn app.main:app --host 0.0.0.0 --port 8000`

### 3) Acesse a aplicação

| Serviço | Endereço |
| ------- | -------- |
| API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| OpenAPI JSON | http://localhost:8000/openapi.json |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

### 4) Parar os containers

```bash
docker compose down
```

Para remover volumes junto com a stack:

```bash
docker compose down -v
```

## Visão geral do projeto

A aplicação expõe um CRUD de usuários com as seguintes características:

- cadastro, consulta, atualização e remoção lógica de usuários;
- validação de dados com Pydantic;
- persistência assíncrona com SQLAlchemy 2 + asyncpg;
- migrations com Alembic;
- cache de leitura com Redis para detalhe e listagem;
- tratamento padronizado de erros;
- arquitetura em camadas para separar API, regra de negócio e acesso a dados.

## Stack utilizada

| Camada | Tecnologia |
| ------ | ---------- |
| API | FastAPI, Uvicorn |
| Validação | Pydantic, pydantic-settings |
| Banco de dados | PostgreSQL |
| ORM | SQLAlchemy 2 async, asyncpg |
| Cache | Redis |
| Migrations | Alembic |
| Qualidade | Ruff, Mypy, Pytest, pytest-asyncio |
| Empacotamento | Poetry |
| Infraestrutura | Docker, Docker Compose |

## Estrutura do repositório

```text
.
├── app/
│   ├── api/              # Rotas e dependências do FastAPI
│   ├── cache/            # Cliente Redis, serviço de cache e chaves
│   ├── constants/        # Constantes compartilhadas da aplicação
│   ├── core/             # Settings e logging
│   ├── db/               # Configuração de banco, sessão e unit of work
│   ├── exceptions/       # Exceções de domínio e handlers globais
│   ├── interfaces/       # Contratos/Protocol das dependências principais
│   ├── models/           # Models SQLAlchemy
│   ├── repositories/     # Acesso a dados
│   ├── schemas/          # Schemas de entrada e saída
│   ├── security/         # Hash de senha
│   ├── services/         # Regras de negócio
│   └── tests/            # Testes automatizados
├── alembic/              # Configuração e versões de migration
├── docker/               # Entrypoint da aplicação no container
├── postman/              # Collection para teste manual da API
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

## Arquitetura

A API segue uma divisão em camadas para facilitar manutenção e testes:

- **routes**: recebem a requisição HTTP e delegam para a service;
- **services**: concentram as regras de negócio da feature;
- **repositories**: fazem o acesso ao banco de dados;
- **db**: centraliza sessão, configuração e unidade transacional;
- **cache**: encapsula o uso do Redis e a estratégia de cache;
- **schemas**: definem contratos de entrada e saída da API;
- **exceptions**: padronizam respostas de erro.

Esse desenho reduz acoplamento entre FastAPI, banco, cache e regras de domínio.

## Variáveis de ambiente

As principais variáveis estão em `.env.example`:

| Variável | Descrição | Exemplo |
| -------- | --------- | ------- |
| `APP_NAME` | Nome exibido na documentação da API | `Jabuti API` |
| `ENVIRONMENT` | Ambiente da aplicação | `development` |
| `DEBUG` | Liga/desliga modo debug | `false` |
| `API_PREFIX` | Prefixo das rotas | `/api/v1` |
| `DATABASE_URL` | URL async do Postgres | `postgresql+asyncpg://jabuti:jabuti@localhost:5432/jabuti` |
| `POSTGRES_USER` | Usuário do Postgres | `jabuti` |
| `POSTGRES_PASSWORD` | Senha do Postgres | `jabuti` |
| `POSTGRES_DB` | Nome do banco | `jabuti` |
| `REDIS_URL` | URL de conexão com Redis | `redis://localhost:6379/0` |
| `REDIS_CACHE_TTL_SECONDS` | TTL padrão do cache | `300` |

No `docker-compose.yml`, a API monta internamente a conexão com Postgres e Redis usando os nomes dos serviços da rede Docker.

## Endpoints principais

Com o prefixo padrão `/api/v1`, os endpoints disponíveis são:

| Método | Rota | Descrição |
| ------ | ---- | --------- |
| `POST` | `/api/v1/users` | Cria um usuário |
| `GET` | `/api/v1/users/{user_id}` | Busca um usuário por ID |
| `GET` | `/api/v1/users?limit=10&offset=0` | Lista usuários paginados |
| `PUT` | `/api/v1/users/{user_id}` | Atualiza um usuário |
| `DELETE` | `/api/v1/users/{user_id}` | Remove logicamente um usuário |

## Contratos da API

### Criação de usuário

Campos esperados em `POST /api/v1/users`:

- `name`
- `email`
- `password`

### Atualização de usuário

Campos aceitos em `PUT /api/v1/users/{user_id}`:

- `name`
- `email`
- `password`
- `active`

### Resposta pública

Os retornos da API expõem:

- `id`
- `name`
- `email`
- `active`
- `created_at`
- `updated_at`

> A senha nunca é retornada pela API.

## Cache com Redis

A aplicação usa Redis para reduzir leituras repetidas no banco de dados.

### Chaves de cache

- `users:detail:{id}`
- `users:list:{limit}:{offset}`

### Estratégia de invalidação

- **create**: invalida listagens;
- **update**: invalida detalhe + listagens;
- **delete**: invalida detalhe + listagens.

A invalidação após escrita é tratada em modo **best-effort**, evitando falha total da operação caso o banco já tenha confirmado a transação e o Redis apresente indisponibilidade transitória.

## Banco de dados e migrations

As migrations são gerenciadas com **Alembic**.

No fluxo Docker, não é necessário executar comandos manualmente: o container da API roda `alembic upgrade head` automaticamente no startup.

A migration atual cria a tabela de usuários, utilizada pela feature principal do projeto.

## Documentação e testes manuais

### Swagger / OpenAPI

Após subir os containers:

- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

### Collection Postman / Insomnia

O repositório inclui uma collection em:

- `postman/Jabuti.postman_collection.json`

Ela pode ser importada tanto no **Postman** quanto no **Insomnia** para validar os endpoints manualmente.

## Qualidade de código

O projeto já está preparado com ferramentas de qualidade e testes automatizados:

- `ruff` para lint;
- `ruff format` para formatação;
- `mypy` para checagem estática de tipos;
- `pytest` para testes.

Mesmo que a execução oficial do projeto seja via Docker, esses comandos existem para manutenção e evolução do código.

## Diferenciais técnicos implementados

- arquitetura em camadas;
- injeção de dependências no FastAPI;
- sessão assíncrona de banco por requisição;
- `UnitOfWork` para explicitar commits de escrita;
- validação centralizada com Pydantic;
- cache Redis desacoplado por interfaces;
- tratamento global e padronizado de exceções;
- configuração centralizada por ambiente com `pydantic-settings`.

## Fluxo resumido da aplicação

1. O cliente chama um endpoint da API.
2. A rota resolve as dependências e obtém um `UserService`.
3. O service aplica as regras de negócio.
4. O repository acessa o PostgreSQL.
5. Leituras podem consultar/preencher cache no Redis.
6. Escritas confirmam transação e invalidam cache quando necessário.

## Próximos pontos de evolução

Algumas melhorias naturais para a continuidade do projeto seriam:

- autenticação/autorização;
- paginação com metadados mais completos;
- observabilidade com métricas e tracing;
- testes de integração com containers dedicados;
- pipeline de CI/CD e deploy automatizado.
