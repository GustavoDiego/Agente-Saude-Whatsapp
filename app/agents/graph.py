"""
Agente de Triagem – ClinicAI
----------------------------------------------
Fluxo principal:
    llm_dialog → (se mensagem final) → llm_extract → extract → persist → END

Objetivo:
    - Conduzir uma conversa natural com o paciente.
    - Só na mensagem final extrair e salvar a triagem.
"""

import json
from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
from app.services.llm import LLMService
from app.schemas.triage import Triage
from app.services.persistence import PersistenceService


class TriageState(TypedDict, total=False):
    """
    Estado compartilhado do agente de triagem.
    """
    conversation_id: str
    user_message: str
    conversation_context: str
    agent_message: str
    internal_reply: str
    triage: Dict[str, Any]


class TriageAgent:
    """
    Agente responsável por orquestrar a conversa com o paciente
    e conduzir a extração da triagem ao final.
    """
    def __init__(self) -> None:
        self.llm = LLMService()
        self.persistence = PersistenceService()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """
        Constrói o grafo de estados que controla o fluxo de diálogo,
        extração de dados e persistência da triagem.
        """
        graph = StateGraph(TriageState)

        async def llm_dialog_node(state: Dict[str, Any]) -> Dict[str, Any]:
            """
            Nó 1 – Conduz diálogo normal com o paciente.
            """
            reply = await self.llm.get_reply(
                state["user_message"],
                state["conversation_id"],
                state.get("conversation_context", "")
            )
            return {**state, "agent_message": reply}

        async def llm_extract_node(state: Dict[str, Any]) -> Dict[str, Any]:
            """
            Nó 2 – Solicita à LLM a extração em JSON
            com base no histórico e na última mensagem.
            """
            prompt = (
                "Extraia as informações abaixo da conversa (histórico + última mensagem). "
                "Responda SOMENTE em JSON.\n\n"
                "{\n"
                '  "queixa_principal": "",\n'
                '  "sintomas": "",\n'
                '  "duracao_frequencia": "",\n'
                '  "intensidade": 0,\n'
                '  "historico": "",\n'
                '  "medidas_tomadas": ""\n'
                "}\n\n"
                f"Histórico:\n{state.get('conversation_context', '')}\n\n"
                f"Última mensagem:\n{state['user_message']}"
            )
            reply = await self.llm.get_reply(prompt, state["conversation_id"])
            return {**state, "internal_reply": reply}

        async def extraction_node(state: Dict[str, Any]) -> Dict[str, Any]:
            """
            Nó 3 – Valida e converte o JSON bruto em objeto estruturado.
            """
            cleaned = (
                state["internal_reply"]
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )
            try:
                triage = Triage.model_validate_json(cleaned)
                state["triage"] = triage.dict(exclude_unset=True)
            except Exception:
                state["triage"] = {}
            return state

        async def persist_node(state: Dict[str, Any]) -> Dict[str, Any]:
            """
            Nó 4 – Persiste a triagem no banco e retorna mensagem final.
            """
            final_message = (
                "Obrigado por compartilhar todas essas informações. "
                "Sua triagem foi registrada e será encaminhada para nossa equipe médica, "
                "que dará continuidade ao seu atendimento. "
                "Lembre-se: este é apenas um pré-atendimento e não substitui uma consulta "
                "com um profissional de saúde."
            )
            triage_data = state.get("triage", {})
            if triage_data:
                await self.persistence.save_triage(state["conversation_id"], triage_data)
            return {**state, "agent_message": final_message}

        def decide_next(state: Dict[str, Any]) -> str:
            """
            Decide se deve iniciar extração ou encerrar após o diálogo.
            """
            final_phrase = "sua triagem foi registrada"
            if final_phrase in state.get("agent_message", "").lower():
                return "llm_extract"
            return END

        graph.add_node("llm_dialog", llm_dialog_node)
        graph.add_node("llm_extract", llm_extract_node)
        graph.add_node("extract", extraction_node)
        graph.add_node("persist", persist_node)

        graph.set_entry_point("llm_dialog")
        graph.add_conditional_edges("llm_dialog", decide_next, {
            "llm_extract": "llm_extract",
            END: END,
        })
        graph.add_edge("llm_extract", "extract")
        graph.add_edge("extract", "persist")
        graph.add_edge("persist", END)

        return graph.compile()

    def get_graph(self) -> StateGraph:
        """
        Retorna o grafo de estados compilado.
        """
        return self.graph
