"""
Fluxo do agente de triagem utilizando LangGraph.

Este módulo define o grafo que orquestra a coleta de informações
do usuário em etapas, guiado pela LLM, até consolidar os dados
necessários para uma triagem inicial estruturada.
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, END
from app.services.llm import LLMService, build_full_prompt
from app.schemas.triage import Triage
from app.services.persistence import PersistenceService


class TriageAgent:
    """
    Agente de triagem baseado em LangGraph.

    Orquestra a coleta das informações necessárias
    (queixa principal, sintomas, duração/frequência, etc.)
    até consolidar um objeto `Triage`.
    """

    def __init__(self) -> None:
        self.llm = LLMService()
        self.persistence = PersistenceService()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """
        Constrói o grafo de estados da triagem.
        Retorna:
            StateGraph: Grafo configurado.
        """
        graph = StateGraph()

        async def llm_node(state: Dict[str, Any]) -> Dict[str, Any]:
            user_message = state["user_message"]
            conversation_context = state.get("conversation_context", "")
            reply = await self.llm.get_reply(user_message, state["conversation_id"], conversation_context)
            return {**state, "agent_reply": reply}

        async def extraction_node(state: Dict[str, Any]) -> Dict[str, Any]:
            try:
                triage = Triage.parse_raw(state["agent_reply"])
                state["triage"] = triage.dict()
                return {**state, "triage_complete": True}
            except Exception:
                return {**state, "triage_complete": False}

        def decide_next(state: Dict[str, Any]) -> str:
            if state.get("triage_complete"):
                return "persist"
            return "llm"

        async def persist_node(state: Dict[str, Any]) -> Dict[str, Any]:
            triage_data = state["triage"]
            await self.persistence.save_triage(state["conversation_id"], triage_data)
            return state

        graph.add_node("llm", llm_node)
        graph.add_node("extract", extraction_node)
        graph.add_node("persist", persist_node)

        graph.set_entry_point("llm")
        graph.add_edge("llm", "extract")
        graph.add_conditional_edges("extract", decide_next, {"llm": "llm", "persist": "persist"})
        graph.add_edge("persist", END)

        return graph

    def get_graph(self) -> StateGraph:
        """Retorna o grafo construído do agente de triagem."""
        return self.graph
