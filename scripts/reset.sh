#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

WITH_FALCO=0
if [ "${1:-}" = "--with-falco" ]; then
  WITH_FALCO=1
fi

if [ "$WITH_FALCO" -eq 1 ]; then
  docker compose -f compose.yaml -f compose.falco.yaml down -v
else
  docker compose down -v
fi

rm -f exports/*
touch exports/.gitkeep
chmod 777 exports

if [ "$WITH_FALCO" -eq 1 ]; then
  docker compose -f compose.yaml -f compose.falco.yaml up -d
  docker compose -f compose.yaml -f compose.falco.yaml ps
else
  docker compose up -d
  docker compose ps
fi
