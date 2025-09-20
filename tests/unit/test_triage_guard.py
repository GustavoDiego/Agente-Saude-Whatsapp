"""
Testes unitários para o serviço de detecção de emergências (triage_guard).

Objetivos:
- Verificar que palavras-chave de emergência são corretamente identificadas.
- Garantir que mensagens normais não sejam sinalizadas como emergência.
- Confirmar que múltiplos gatilhos também retornam a resposta de emergência.
"""

import pytest
from app.services.triage_guard import check_emergency
from app.constants.emergencies import EMERGENCY_MESSAGE


@pytest.mark.asyncio
async def test_detects_single_emergency_keyword():
    """
    Deve identificar quando a mensagem contém uma palavra-chave de emergência.
    """
    user_message = "Estou com dor no peito desde ontem"
    result = check_emergency(user_message)
    assert result == EMERGENCY_MESSAGE


@pytest.mark.asyncio
async def test_does_not_flag_normal_message():
    """
    Não deve sinalizar mensagens que não contêm palavras de emergência.
    """
    user_message = "Estou apenas com dor de cabeça leve"
    result = check_emergency(user_message)
    assert result is None


@pytest.mark.asyncio
async def test_detects_multiple_emergency_keywords():
    """
    Deve retornar a mensagem de emergência mesmo quando múltiplas palavras-chave aparecem.
    """
    user_message = "Tive um desmaio e agora sinto falta de ar"
    result = check_emergency(user_message)
    assert result == EMERGENCY_MESSAGE
