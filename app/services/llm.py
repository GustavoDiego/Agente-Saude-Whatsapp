"""
Módulo responsável pela integração com o modelo de linguagem (LLM).
Define utilitários para prompts dinâmicos e uma classe de serviço
que abstrai as chamadas ao Gemini.
"""

import pathlib
import json
from typing import Any, Dict, Optional

from app.constants import emergencies
from app.schemas.triage import Triage
from app.settings import settings

from langchain_google_genai import ChatGoogleGenerativeAI


BASE_DIR = pathlib.Path(__file__).resolve().parent.parent


def load_system_prompt() -> str:
    """Carrega o prompt de sistema que define a persona e missão do agente."""
    prompt_path = BASE_DIR / "prompts" / "system_triage.txt"
    with open(prompt_path, encoding="utf-8") as f:
        return f.read().strip()


def build_emergency_prompt() -> str:
    """Constrói dinamicamente o prompt de regras de emergência."""
    keywords = ", ".join(emergencies.EMERGENCY_KEYWORDS)
    return (
        "Regras de Emergência:\n"
        "Se a mensagem do usuário contiver sinais de urgência médica, como "
        f"{keywords}, interrompa a triagem imediatamente e responda:\n"
        "\"Entendi. Seus sintomas podem indicar uma situação de emergência. "
        "Por favor, procure o pronto-socorro mais próximo ou ligue para o 192 imediatamente.\""
    )


def get_triage_schema() -> Dict[str, Any]:
    """Retorna o JSON Schema da triagem baseado no modelo Pydantic."""
    return Triage.model_json_schema()


def get_llm() -> ChatGoogleGenerativeAI:
    """Inicializa o cliente Gemini configurado."""
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.3,
        google_api_key=settings.GOOGLE_API_KEY,
    )


def build_full_prompt(user_message: str, conversation_context: str = "") -> str:
    """Monta o prompt completo para enviar ao LLM."""
    system_prompt = load_system_prompt()
    emergency_prompt = build_emergency_prompt()
    triage_schema = json.dumps(get_triage_schema(), indent=2, ensure_ascii=False)

    return (
        f"{system_prompt}\n\n"
        f"{emergency_prompt}\n\n"
        "Estrutura esperada da triagem (JSON Schema):\n"
        f"{triage_schema}\n\n"
        "Histórico da conversa:\n"
        f"{conversation_context}\n\n"
        "Mensagem do usuário:\n"
        f"{user_message}"
    )


class LLMService:
    """
    Serviço de integração com o LLM.
    Responsável por orquestrar prompts e obter respostas.
    """

    def __init__(self) -> None:
        self.client = get_llm()

    async def get_reply(
        self, user_message: str, session_id: Optional[str] = None, conversation_context: str = ""
    ) -> str:
        """
        Obtém a resposta do LLM para a mensagem do usuário.

        Args:
            user_message (str): Última mensagem do usuário.
            session_id (Optional[str]): Identificador da sessão/conversa.
            conversation_context (str): Histórico resumido da conversa.

        Returns:
            str: Resposta gerada pelo modelo.
        """
        prompt = build_full_prompt(user_message, conversation_context)
        response = await self.client.ainvoke(prompt)
        return response.content
