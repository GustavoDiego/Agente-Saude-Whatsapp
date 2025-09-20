#!/usr/bin/env bash


PORT="${APP_PORT:-8000}"
NGROK_BIN="${NGROK_BIN:-ngrok}"
AUTHTOKEN="${NGROK_AUTHTOKEN:-}"

if [ -n "$AUTHTOKEN" ]; then
  $NGROK_BIN config add-authtoken "$AUTHTOKEN"
fi

echo "Iniciando ngrok na porta $PORT..."
$NGROK_BIN http $PORT
