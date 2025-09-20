from typing import List, Dict, Any
from app.services.persistence import PersistenceService
from app.schemas.chat import ChatRequest, ChatResponse


class ChatRepository:
    """
    Repositório responsável por operações de leitura e escrita
    relacionadas ao histórico de mensagens.
    """

    def __init__(self, persistence: PersistenceService):
        self.persistence = persistence

    async def save_message(self, request: ChatRequest, response: ChatResponse) -> str:
        """
        Persiste uma mensagem e a resposta do agente.

        Args:
            request (ChatRequest): Mensagem recebida do usuário.
            response (ChatResponse): Resposta do agente.

        Returns:
            str: ID do documento salvo.
        """
        return await self.persistence.save_message(request, response)

    async def get_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Recupera todo o histórico de mensagens de uma conversa.

        Args:
            conversation_id (str): Identificador da conversa.

        Returns:
            List[Dict[str, Any]]: Lista de mensagens.
        """
        return await self.persistence.get_conversation(conversation_id)
