"""
Testes de integração para fluxo de emergência via webhook.

Objetivos:
- Detectar gatilhos de emergência nas mensagens recebidas.
- Garantir que a resposta enviada ao usuário seja a mensagem de alerta padrão.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.constants.emergencies import EMERGENCY_MESSAGE

client = TestClient(app)


@pytest.mark.asyncio
async def test_webhook_detects_emergency(monkeypatch):
    """
    Deve identificar uma mensagem de emergência e responder com EMERGENCY_MESSAGE.
    """


    async def fake_send_message(payload):
        return {"messages": [{"id": "wamid.fake"}], "response_text": payload.text["body"]}

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
                                    "text": {"body": "Estou com falta de ar e dor no peito"},
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
    assert data["last_response"] == EMERGENCY_MESSAGE
