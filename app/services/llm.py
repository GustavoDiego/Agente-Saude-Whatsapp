"""
Serviço LLM – ClinicAI
----------------------
Responsável por:
- Carregar prompts do sistema.
- Construir mensagens de emergência.
- Fornecer schema esperado da triagem.
- Instanciar e chamar o modelo de linguagem (Gemini).
- Montar o prompt completo com histórico e mensagem do usuário.
- Retornar respostas em JSON padronizado.
"""

import pathlib
import json
from typing import Any, Dict, Optional

from app.constants import emergencies
from app.schemas.triage import Triage
from app.settings import settings

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent


def load_system_prompt() -> str:
    """
    Carrega o prompt principal do sistema a partir do arquivo.
    """
    prompt_path = BASE_DIR / "prompts" / "system_triage.txt"
    with open(prompt_path, encoding="utf-8") as f:
        return f.read().strip()


def build_emergency_prompt() -> str:
    """
    Constrói instrução para detectar palavras-chave de emergência
    e interromper a triagem caso sejam identificadas.
    """
    keywords = ", ".join(emergencies.EMERGENCY_KEYWORDS)
    return (
        "Regras de Emergência:\n"
        "Se a mensagem do usuário contiver sinais de urgência médica, como "
        f"{keywords}, interrompa a triagem imediatamente e responda:\n"
        "\"Entendi. Seus sintomas podem indicar uma situação de emergência. "
        "Por favor, procure o pronto-socorro mais próximo ou ligue para o 192 imediatamente.\""
    )


def get_triage_schema() -> Dict[str, Any]:
    """
    Retorna o schema em JSON da triagem definido no modelo Pydantic.
    """
    return Triage.model_json_schema()


def get_llm() -> ChatGoogleGenerativeAI:
    """
    Instancia o modelo de linguagem Gemini via LangChain.
    """
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
        google_api_key=settings.GOOGLE_API_KEY,
    )


def build_full_prompt(user_message: str, conversation_context: str = "") -> str:
    """
    Monta o prompt completo enviado à LLM,
    incluindo instruções do sistema, regras de emergência,
    schema da triagem, histórico da conversa e mensagem atual do usuário.
    """
    system_prompt = load_system_prompt()
    emergency_prompt = build_emergency_prompt()
    triage_schema = json.dumps(get_triage_schema(), indent=2, ensure_ascii=False)

    return (
        f"{system_prompt}\n\n"
        f"{emergency_prompt}\n\n"
        "IMPORTANTE:\n"
        "- Use EXATAMENTE os nomes de campos do schema abaixo em português.\n"
        "- Nunca use null. Se não houver informação, use string vazia ('') para textos e 0 para intensidade.\n\n"
        "Estrutura esperada da triagem (JSON Schema):\n"
        f"{triage_schema}\n\n"
        "Histórico da conversa:\n"
        f"{conversation_context}\n\n"
        "Mensagem do usuário:\n"
        f"{user_message}"
    )


class LLMService:
    """
    Serviço que encapsula a interação com o modelo LLM,
    cuidando do histórico e do formato da resposta.
    """
    def __init__(self) -> None:
        self.client = get_llm()

    async def get_reply(
        self,
        user_message: str,
        session_id: Optional[str] = None,
        history_docs: Optional[list] = None,
    ) -> str:
        """
        Retorna a resposta da LLM para uma mensagem do usuário,
        incluindo contexto anterior se disponível.
        """
        system_prompt = load_system_prompt()
        emergency_prompt = build_emergency_prompt()
        triage_schema = json.dumps(get_triage_schema(), indent=2, ensure_ascii=False)

        messages = [
            SystemMessage(
                content=(
                    f"{system_prompt}\n\n"
                    f"{emergency_prompt}\n\n"
                    "IMPORTANTE:\n"
                    "- Sempre retorne JSON usando EXATAMENTE estes campos em português (iguais ao schema).\n"
                    "- Nunca use null. Se não houver informação, use string vazia ('') para textos e 0 para intensidade.\n\n"
                    f"{triage_schema}"
                )
            )
        ]

        if history_docs:
            for doc in history_docs:
                if "user_message" in doc:
                    messages.append(HumanMessage(content=doc["user_message"]))
                if "agent_message" in doc:
                    messages.append(AIMessage(content=doc["agent_message"]))

        messages.append(HumanMessage(content=user_message))

        response = await self.client.ainvoke(messages)
        reply = response.content.strip()

        if reply.lower().startswith("agente:"):
            reply = reply.split(":", 1)[1].strip()

        return reply
