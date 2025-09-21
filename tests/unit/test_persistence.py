"""
Testes unitários para o serviço de persistência (PersistenceService).

Objetivos:
- Verificar se mensagens são salvas e recuperadas corretamente.
- Validar que triagens estruturadas são persistidas e retornadas.
"""

import pytest
from datetime import datetime
from app.services.persistence import PersistenceService
from app.schemas.chat import ChatRequest, ChatResponse


@pytest.mark.asyncio
async def test_save_and_get_message(db, monkeypatch):
    """
    Deve salvar uma mensagem de usuário + resposta do agente
    e recuperá-la corretamente.
    """

    service = PersistenceService()
    service.db = db
    service.messages = db["messages"]

    chat_request = ChatRequest(
        conversation_id="conv1",
        user_id="user123",
        channel="web",
        message="Estou com dor de cabeça"
    )
    chat_response = ChatResponse(
        conversation_id="conv1",
        response="Entendi, pode me contar mais?",
        timestamp=datetime.utcnow(),
    )

    inserted_id = await service.save_message(chat_request, chat_response)
    assert inserted_id is not None

    messages = await service.get_conversation("conv1")
    assert len(messages) == 1
    assert messages[0]["user_message"] == "Estou com dor de cabeça"
    assert messages[0]["agent_message"] == "Entendi, pode me contar mais?"


@pytest.mark.asyncio
async def test_save_and_get_triage(db):
    """
    Deve salvar uma triagem estruturada e recuperá-la corretamente.
    """
    service = PersistenceService()
    service.db = db
    service.triages = db["triages"]

    triage_data = {
        "queixa_principal": "Dor abdominal",
        "sintomas": "Dor constante na região inferior",
        "duracao_frequencia": "2 dias, intermitente",
        "intensidade": "7",
        "historico": "Nenhuma condição prévia",
        "medidas_tomadas": "Tomou analgésico sem melhora",
    }

    inserted_id = await service.save_triage("conv2", triage_data)
    assert inserted_id is not None

    triage = await service.get_triage("conv2")
    assert triage is not None
    assert triage["data"]["queixa_principal"] == "Dor abdominal"
    assert triage["data"]["intensidade"] == "7"
