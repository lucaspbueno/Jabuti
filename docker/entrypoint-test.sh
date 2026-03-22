#!/bin/sh
# -----------------------------------------------------------------------------
# Entrypoint SOMENTE para rodar a suíte de testes dentro do container.
#
# NÃO é o ENTRYPOINT padrão da imagem (esse papel continua com entrypoint.sh,
# que aplica migrações e sobe o Uvicorn). Use este arquivo apenas ao invocar
# explicitamente, por exemplo:
#
#   docker compose run --rm --no-deps --entrypoint /entrypoint-test.sh api
#
# Motivo: a imagem instala só dependências de produção (--only main no build).
# O pytest e o restante do grupo "dev" entram aqui com "poetry install --with dev".
# -----------------------------------------------------------------------------

set -e

# Garante pytest, httpx, ruff, etc. (grupo dev do pyproject.toml).
poetry install --with dev -q

# exec substitui o processo shell pelo pytest (sinalização e código de saída corretos).
exec poetry run pytest -vv
