#!/usr/bin/env bash

if [ ! -f ".env" ]; then
  echo "ERRO: arquivo .env não encontrado."
  exit 1
fi

export $(grep -v '^#' .env | xargs)
echo "Variáveis do .env carregadas no ambiente."
