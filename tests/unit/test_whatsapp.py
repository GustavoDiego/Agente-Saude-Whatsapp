"""
Testes unitários para o serviço de integração com WhatsApp (WhatsAppService).

Objetivos:
- Verificar que mensagens são enviadas corretamente à API do WhatsApp.
- Validar que erros de rede ou credenciais incorretas levantam exceções.
"""

import os
import pytest
import respx
from httpx import Response, RequestError

from app.services.whatsapp import WhatsAppService
from app.schemas.whatsapp import WhatsAppSendMessage


@pytest.mark.asyncio
async def test_send_message_success(monkeypatch):
    """
    Deve enviar uma mensagem com sucesso e retornar JSON da API do WhatsApp.
    """
    # Configurar env vars fake
    monkeypatch.setenv("WHATSAPP_PHONE_NUMBER_ID", "123456789")
    monkeypatch.setenv("WHATSAPP_ACCESS_TOKEN", "fake_token")

    service = WhatsAppService()

    payload = WhatsAppSendMessage(to="5581991113682", text={"body": "Olá, teste!"})

    with respx.mock(assert_all_called=True) as http_mock:
        route = http_mock.post("https://graph.facebook.com/v22.0/123456789/messages").mock(
            return_value=Response(200, json={"messages": [{"id": "wamid.fake"}]})
        )

        result = await service.send_message(payload)

        assert route.called
        assert result["messages"][0]["id"] == "wamid.fake"


@pytest.mark.asyncio
async def test_send_message_raises_on_error(monkeypatch):
    """
    Deve levantar erro se a API do WhatsApp retornar falha.
    """
    monkeypatch.setenv("WHATSAPP_PHONE_NUMBER_ID", "123456789")
    monkeypatch.setenv("WHATSAPP_ACCESS_TOKEN", "fake_token")

    service = WhatsAppService()
    payload = WhatsAppSendMessage(to="5581991113682", text={"body": "Falha de rede"})

    with respx.mock(assert_all_called=True) as http_mock:
        http_mock.post("https://graph.facebook.com/v22.0/123456789/messages").mock(
            return_value=Response(401, json={"error": "Unauthorized"})
        )

        with pytest.raises(Exception):
            await service.send_message(payload)


def test_init_without_env(monkeypatch):
    """
    Deve levantar ValueError se env vars obrigatórias não estiverem definidas.
    """
    monkeypatch.delenv("WHATSAPP_PHONE_NUMBER_ID", raising=False)
    monkeypatch.delenv("WHATSAPP_ACCESS_TOKEN", raising=False)

    with pytest.raises(ValueError):
        WhatsAppService()
