from datetime import datetime
from typing import Any, Dict, Optional, List
from motor.motor_asyncio import AsyncIOMotorClient
from app.schemas.chat import ChatRequest, ChatResponse
from app.settings import settings


class PersistenceService:
    """
    Serviço responsável pela persistência de dados no MongoDB.

    Estrutura:
        - Collection `messages`: histórico detalhado das interações
          entre usuário e agente (user_message + agent_message).
        - Collection `triages`: resumo final estruturado da triagem,
          armazenado ao término da coleta de informações.
    """

    def __init__(self) -> None:
        """
        Inicializa a conexão com o MongoDB utilizando variáveis de ambiente
        definidas em `settings`. Se não configurado, usa valores padrão.
        """
        self.client = AsyncIOMotorClient(settings.MONGO_URI)
        self.db = self.client[settings.MONGO_DB]
        self.messages = self.db["messages"]
        self.triages = self.db["triages"]

    async def save_message(self, chat_request: ChatRequest, chat_response: ChatResponse) -> str:
        """
        Salva uma interação (mensagem do usuário + resposta do agente).

        Args:
            chat_request (ChatRequest): Mensagem enviada pelo usuário.
            chat_response (ChatResponse): Resposta gerada pelo agente.

        Returns:
            str: ID do documento persistido.
        """
        doc = {
            "conversation_id": chat_request.conversation_id,
            "user_id": chat_request.user_id,
            "channel": chat_request.channel,
            "user_message": chat_request.message,
            "agent_message": chat_response.response,
            "timestamp": datetime.utcnow(),
        }
        result = await self.messages.insert_one(doc)
        return str(result.inserted_id)

    async def get_conversation(self, conversation_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Recupera todas as mensagens de uma conversa, ordenadas por tempo.

        Args:
            conversation_id (str): Identificador único da conversa.
            limit (int): Número máximo de mensagens a retornar (default: 100).

        Returns:
            List[Dict[str, Any]]: Lista de mensagens trocadas.
        """
        cursor = (
            self.messages.find({"conversation_id": conversation_id})
            .sort("timestamp", 1)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def save_triage(self, conversation_id: str, triage_data: Dict[str, Any]) -> str:
        """
        Salva o resumo estruturado da triagem (já consolidado).

        Args:
            conversation_id (str): Identificador único da conversa.
            triage_data (Dict[str, Any]): Dados estruturados da triagem,
                                          conforme extração pelo agente.

        Returns:
            str: ID do documento persistido.
        """
        doc = {
            "conversation_id": conversation_id,
            "data": triage_data,
            "created_at": datetime.utcnow(),
        }
        result = await self.triages.insert_one(doc)
        return str(result.inserted_id)

    async def get_triage(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Recupera a triagem final associada a uma conversa.

        Args:
            conversation_id (str): Identificador único da conversa.

        Returns:
            Optional[Dict[str, Any]]: Documento da triagem, se existir.
        """
        return await self.triages.find_one({"conversation_id": conversation_id})
