"""
Arquivo de configuração de testes para pytest.

Define fixtures reutilizáveis para:
- MongoDB em memória (motor mockado).
- Mock de chamadas HTTP externas (WhatsApp, Gemini).
"""

import pytest
import respx
from httpx import Response
from motor.motor_asyncio import AsyncIOMotorClient
from mongomock_motor import AsyncMongoMockClient


@pytest.fixture(scope="session")
def mongo_client() -> AsyncIOMotorClient:
    """
    Fornece um cliente MongoDB em memória para os testes.
    Usa `mongomock_motor`, que implementa a interface do Motor.
    """
    return AsyncMongoMockClient()


@pytest.fixture
def db(mongo_client) -> AsyncIOMotorClient:
    """
    Retorna um banco de dados isolado para cada teste.
    """
    return mongo_client["clinicai_test"]


@pytest.fixture(autouse=True)
def http_mock():
    """
    Ativa respx para mockar chamadas HTTP externas durante os testes.
    Reseta automaticamente a cada teste.
    """
    with respx.mock(assert_all_called=False) as respx_mock:
        yield respx_mock


@pytest.fixture
def mock_whatsapp_send(http_mock):
    """
    Mock para envio de mensagens ao WhatsApp Cloud API.
    Sempre retorna `{"messages": [{"id": "fake_wamid"}]}`.
    """
    http_mock.post("https://graph.facebook.com/v22.0/123456789/messages").mock(
        return_value=Response(200, json={"messages": [{"id": "fake_wamid"}]})
    )
    return http_mock


@pytest.fixture
def mock_gemini_chat(http_mock):
    """
    Mock para chamadas ao Gemini (LangChain).
    Simula resposta básica de IA.
    """
    http_mock.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent").mock(
        return_value=Response(200, json={
            "candidates": [{
                "content": {"parts": [{"text": "Simulação de resposta da IA"}]}
            }]
        })
    )
    return http_mock
