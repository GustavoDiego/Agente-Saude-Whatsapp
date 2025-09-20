"""
Testes de integração para o fluxo do webhook do WhatsApp.

Objetivos:
- Verificar se a rota de verificação do webhook responde corretamente ao desafio.
- Garantir que uma mensagem recebida seja processada e uma resposta seja enviada.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.settings import settings

client = TestClient(app)


def test_webhook_verification():
    """
    Deve retornar o hub.challenge se o token for válido.
    O token é lido automaticamente de settings (variável de ambiente).
    """
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": settings.WHATSAPP_VERIFY_TOKEN,
        "hub.challenge": "12345",
    }

    response = client.get("/webhook/whatsapp", params=params)
    assert response.status_code == 200
    assert response.text == "12345"


@pytest.mark.asyncio
async def test_webhook_receive_message(monkeypatch):
    """
    Deve processar mensagem recebida e enviar resposta simulada ao usuário.
    """

    async def fake_send_message(payload):
        return {"messages": [{"id": "wamid.fake"}]}

    monkeypatch.setattr("app.services.whatsapp.WhatsAppService.send_message", fake_send_message)

    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "test_entry",
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "from": "5581991113682",
                                    "id": "wamid.test",
                                    "timestamp": "1690000000",
                                    "text": {"body": "Estou com dor no peito"},
                                    "type": "text",
                                }
                            ]
                        }
                    }
                ],
            }
        ],
    }

    response = client.post("/webhook/whatsapp", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
