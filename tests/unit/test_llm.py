"""
Testes unitários para o serviço de integração com LLM (llm.py).

Objetivos:
- Garantir que o prompt de sistema seja carregado corretamente.
- Validar a construção dinâmica do prompt completo (persona + emergência + schema + contexto).
- Confirmar que o schema JSON da triagem é coerente com o modelo Pydantic.
"""

import json
import pathlib

import pytest
from app.services import llm
from app.schemas.triage import TriageData


@pytest.mark.asyncio
async def test_load_system_prompt(tmp_path, monkeypatch):
    """
    Deve carregar corretamente o conteúdo do arquivo system_triage.txt.
    """

    prompt_file = tmp_path / "system_triage.txt"
    prompt_file.write_text("Persona de teste", encoding="utf-8")

    monkeypatch.setattr(llm, "BASE_DIR", tmp_path)

    result = llm.load_system_prompt()
    assert result == "Persona de teste"


@pytest.mark.asyncio
async def test_build_emergency_prompt_includes_keywords():
    """
    Deve incluir as palavras-chave de emergência no prompt.
    """
    result = llm.build_emergency_prompt()
    assert "dor no peito" in result
    assert "ligue para o 192" in result


@pytest.mark.asyncio
async def test_get_triage_schema_matches_pydantic():
    """
    O schema JSON retornado deve ser compatível com o modelo Pydantic TriageData.
    """
    schema = llm.get_triage_schema()
    expected_schema = TriageData.model_json_schema()


    for field in expected_schema["properties"].keys():
        assert field in schema["properties"]


@pytest.mark.asyncio
async def test_build_full_prompt_contains_all_sections(monkeypatch):
    """
    O prompt final deve conter: persona, regras de emergência, schema e mensagem do usuário.
    """

    monkeypatch.setattr(llm, "load_system_prompt", lambda: "Persona de Teste")
    monkeypatch.setattr(llm, "build_emergency_prompt", lambda: "Regras de Emergência simuladas")

    user_message = "Tenho dor no peito"
    conversation_context = "Histórico anterior de conversa"

    prompt = llm.build_full_prompt(user_message, conversation_context)

    assert "Persona de Teste" in prompt
    assert "Regras de Emergência simuladas" in prompt
    assert "Histórico anterior de conversa" in prompt
    assert "Tenho dor no peito" in prompt
    assert "Estrutura esperada da triagem" in prompt
    assert json.dumps(llm.get_triage_schema(), ensure_ascii=False)[:50] in prompt
