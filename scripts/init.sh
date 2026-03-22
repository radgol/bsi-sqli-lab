## `scripts/init.sh`

```bash
#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

WITH_FALCO=0
if [ "${1:-}" = "--with-falco" ]; then
  WITH_FALCO=1
fi

if [ ! -f .env ]; then
  cp .env.example .env
fi

mkdir -p exports
touch exports/.gitkeep
chmod 777 exports

if [ "$WITH_FALCO" -eq 1 ]; then
  docker compose -f compose.yaml -f compose.falco.yaml pull
  docker compose -f compose.yaml -f compose.falco.yaml up -d
  docker compose -f compose.yaml -f compose.falco.yaml ps
else
  docker compose pull
  docker compose up -d
  docker compose ps
fi
