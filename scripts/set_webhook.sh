#!/usr/bin/env bash

APP_ID="${APP_ID:-your_app_id}"
APP_SECRET="${APP_SECRET:-your_app_secret}"
VERIFY_TOKEN="${WHATSAPP_VERIFY_TOKEN:-your_verify_token}"
ACCESS_TOKEN="${WHATSAPP_ACCESS_TOKEN:-your_access_token}"
CALLBACK_URL="${CALLBACK_URL:-https://xxxx.ngrok-free.app/webhook/whatsapp}"

if [ -z "$ACCESS_TOKEN" ]; then
  echo "ERRO: WHATSAPP_ACCESS_TOKEN não definido no ambiente."
  exit 1
fi

echo "Configurando webhook para o aplicativo $APP_ID..."

curl -X POST "https://graph.facebook.com/v22.0/$APP_ID/subscriptions" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "object=whatsapp_business_account" \
  -d "callback_url=$CALLBACK_URL" \
  -d "fields=messages" \
  -d "verify_token=$VERIFY_TOKEN"
