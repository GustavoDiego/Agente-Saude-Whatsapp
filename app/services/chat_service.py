from datetime import datetime
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm import LLMService
from app.services.persistence import PersistenceService
from app.services.triage_guard import TriageGuard
from app.agents.graph import TriageAgent
import uuid


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
            print(msg)
            if any(keyword in msg["agent_message"].lower() for keyword in [
                "procure imediatamente o pronto-socorro",
                "Sua triagem foi registrada e será encaminhada para nossa equipe médica"
            ]):
                return []

        if cutoff_index is not None:
            return history[cutoff_index + 1 :]
        return history

    async def process_message(self, payload: ChatRequest) -> ChatResponse:
        """
        Processa uma mensagem recebida do usuário:
        - Gera um conversation_id interno se vier None.
        - Salva a mensagem no histórico.
        - Verifica emergência.
        - Chama o grafo de triagem.
        - Persiste a resposta.
        - Retorna conversation_id=None ao front quando a conversa encerrar.
        """
        # 1) Sempre trabalhe com um conv_id interno (gera se vier None)
        conv_id = payload.conversation_id or str(uuid.uuid4())

        # Garantir que o payload usado na persistência contenha o conv_id
        payload = payload.model_copy(update={"conversation_id": conv_id})

        # 2) Salvar mensagem do usuário
        user_response = ChatResponse(
            conversation_id=conv_id,
            response=payload.message,
            timestamp=datetime.utcnow(),
        )
        await self.persistence.save_message(payload, user_response)

        # 3) Emergência
        if self.guard.is_emergency(payload.message):
            response_text = (
                "Entendi. Seus sintomas podem indicar uma situação de emergência. "
                "Por favor, procure imediatamente o pronto-socorro mais próximo ou ligue para o 192."
            )
            # Persiste a resposta com conv_id interno
            persisted = ChatResponse(
                conversation_id=conv_id,
                response=response_text,
                timestamp=datetime.utcnow(),
            )
            await self.persistence.save_message(payload, persisted)

            # Retorna para o front com conversation_id=None (encerra a conversa no cliente)
            return ChatResponse(
                conversation_id=None,
                response=response_text,
                timestamp=persisted.timestamp,
            )

        # 4) Recuperar histórico relevante e executar grafo
        history_docs = await self._get_relevant_history(conv_id)

        graph = self.triage_agent.get_graph()
        try:
            result_state = await graph.ainvoke(
                {
                    "conversation_id": conv_id,
                    "user_message": payload.message,
                    "conversation_context": history_docs,
                },
                config={"recursion_limit": 5},
            )
            response_text = (
                result_state.get("agent_message")
                or result_state.get("agent_reply")
                or "Ok, estou aguardando sua resposta."
            )
        except Exception as e:
            if str(e) == "__end__":
                response_text = (
                    (locals().get("result_state") or {}).get("agent_message")
                    or (locals().get("result_state") or {}).get("agent_reply")
                    or "Ok, estou aguardando sua resposta."
                )
            else:
                print(f"Erro no grafo de triagem: {str(e)}")
                response_text = (
                    "Desculpe, houve um erro ao processar sua triagem. "
                    "Pode reformular sua mensagem?"
                )

        # 5) Detectar encerramento (mensagem final de triagem registrada)
        is_close = "sua triagem foi registrada" in response_text.lower()

        # Persiste SEMPRE com conv_id interno
        persisted_agent = ChatResponse(
            conversation_id=conv_id,
            response=response_text,
            timestamp=datetime.utcnow(),
        )
        await self.persistence.save_message(payload, persisted_agent)

        if is_close:
           

            # Retorna conversation_id=None ao front para ele iniciar uma nova numa próxima mensagem
            return ChatResponse(
                conversation_id=None,
                response=response_text,
                timestamp=persisted_agent.timestamp,
            )

        # Caso normal (conversa segue com o mesmo conv_id)
        return ChatResponse(
            conversation_id=conv_id,
            response=response_text,
            timestamp=persisted_agent.timestamp,
        )
