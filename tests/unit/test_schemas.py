"""
Testes unitários para schemas Pydantic usados no agente.

Objetivos:
- Garantir que os modelos aceitam dados válidos e rejeitam inválidos.
- Validar campos obrigatórios e opcionais.
- Confirmar que validações específicas (ex: intensidade entre 0 e 10) funcionam.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.triage import TriageData
from app.schemas.whatsapp import WhatsAppSendMessage


def test_chat_request_valid():
    """
    Deve instanciar ChatRequest com dados válidos.
    """
    req = ChatRequest(
        conversation_id="conv123",
        user_id="user123",
        channel="web",
        message="Tenho dor de cabeça há 2 dias",
    )
    assert req.conversation_id == "conv123"
    assert req.message.startswith("Tenho")


def test_chat_request_missing_required():
    """
    Deve falhar se faltar campo obrigatório em ChatRequest.
    """
    with pytest.raises(ValidationError):
        ChatRequest(channel="web", message="Teste")


def test_chat_response_default_timestamp():
    """
    ChatResponse deve preencher timestamp automaticamente.
    """
    resp = ChatResponse(conversation_id="conv123", response="Tudo bem, me conte mais")
    assert isinstance(resp.timestamp, datetime)


def test_triage_data_valid():
    """
    Deve validar corretamente dados de triagem válidos.
    """
    triage = TriageData(
        queixa_principal="Dor abdominal",
        sintomas="Dor constante na região inferior",
        duracao_frequencia="2 dias",
        intensidade=7,
        historico="Nenhum",
        medidas_tomadas="Tomou analgésico",
    )
    assert triage.intensidade == 7


def test_triage_data_invalid_intensity():
    """
    Deve falhar se intensidade estiver fora do intervalo 0-10.
    """
    with pytest.raises(ValidationError):
        TriageData(
            queixa_principal="Dor",
            sintomas="Muito forte",
            duracao_frequencia="Hoje",
            intensidade=15, 
        )


def test_whatsapp_send_message_defaults():
    """
    WhatsAppSendMessage deve preencher campos padrão corretamente.
    """
    msg = WhatsAppSendMessage(to="5581991113682", text={"body": "Olá"})
    assert msg.messaging_product == "whatsapp"
    assert msg.type == "text"
    assert msg.text["body"] == "Olá"
