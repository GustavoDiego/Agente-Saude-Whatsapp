from datetime import datetime
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm import LLMService
from app.services.persistence import PersistenceService
from app.services.triage_guard import TriageGuard
from app.agents.graph import TriageAgent


class ChatService:
    """
    Serviço responsável por orquestrar o fluxo do chat de triagem.

    Responsabilidades:
    - Persistir todas as mensagens do usuário e do agente.
    - Detectar situações de emergência via TriageGuard.
    - Acionar o grafo de triagem (TriageAgent) para conduzir a coleta estruturada.
    - Controlar o momento de persistência final da triagem no banco de dados.
    """

    def __init__(
        self,
        llm_client: LLMService = LLMService(),
        persistence: PersistenceService = PersistenceService(),
        guard: TriageGuard = TriageGuard(),
        triage_agent: TriageAgent = TriageAgent(),
    ):
        self.llm_client = llm_client
        self.persistence = persistence
        self.guard = guard
        self.triage_agent = triage_agent
    async def _get_relevant_history(self, conversation_id: str):
        history = await self.persistence.get_conversation(conversation_id, limit=50)

        cutoff_index = None
        for i, msg in reversed(list(enumerate(history))):
            if any(keyword in msg["response"].lower() for keyword in [
                "procure imediatamente o pronto-socorro",
                "Sua triagem foi registrada e será encaminhada para nossa equipe médica"
            ]):
                cutoff_index = i
                break

        if cutoff_index is not None:
            return history[cutoff_index + 1 :]
        return history

    async def process_message(self, payload: ChatRequest) -> ChatResponse:
        """
        Processa uma mensagem recebida do usuário:
        - Salva a mensagem no histórico.
        - Verifica se é uma situação de emergência.
        - Encaminha ao grafo de triagem para gerar a resposta do agente.
        - Persiste a resposta no histórico.
        """
        user_response = ChatResponse(
            conversation_id=payload.conversation_id,
            response=payload.message,
            timestamp=datetime.utcnow(),
        )
        await self.persistence.save_message(payload, user_response)

        if self.guard.is_emergency(payload.message):
            response_text = (
                "Entendi. Seus sintomas podem indicar uma situação de emergência. "
                "Por favor, procure imediatamente o pronto-socorro mais próximo ou ligue para o 192."
            )
            agent_response = ChatResponse(
                conversation_id=payload.conversation_id,
                response=response_text,
                timestamp=datetime.utcnow(),
            )
            await self.persistence.save_message(payload, agent_response)
            return agent_response

        history_docs = await self._get_relevant_history(payload.conversation_id)

        graph = self.triage_agent.get_graph()

        try:
            result_state = await graph.ainvoke(
                {
                    "conversation_id": payload.conversation_id,
                    "user_message": payload.message,
                    "conversation_context": history_docs,
                },
                config={"recursion_limit": 5},
            )
            response_text = result_state.get("agent_message") or "Ok, estou aguardando sua resposta."

        except Exception as e:
            if str(e) == "__end__":
                response_text = (
                    (locals().get("result_state") or {}).get("agent_message")
                    or (locals().get("result_state") or {}).get("agent_reply")
                    or "Ok, estou aguardando sua resposta."
                )
            else:
                response_text = (
                    "Desculpe, houve um erro ao processar sua triagem. "
                    "Pode reformular sua mensagem?"
                )

        agent_response = ChatResponse(
            conversation_id=payload.conversation_id,
            response=response_text,
            timestamp=datetime.utcnow(),
        )
        await self.persistence.save_message(payload, agent_response)

        return agent_response
