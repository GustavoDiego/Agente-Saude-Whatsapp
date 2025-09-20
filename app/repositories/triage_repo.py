from typing import Dict, Any, Optional
from app.services.persistence import PersistenceService


class TriageRepository:
    """
    Repositório responsável por operações de leitura e escrita
    relacionadas às triagens estruturadas.
    """

    def __init__(self, persistence: PersistenceService):
        self.persistence = persistence

    async def save(self, conversation_id: str, triage_data: Dict[str, Any]) -> str:
        """
        Salva os dados estruturados de uma triagem.

        Args:
            conversation_id (str): Identificador da conversa.
            triage_data (Dict[str, Any]): Informações coletadas.

        Returns:
            str: ID do documento salvo.
        """
        return await self.persistence.save_triage(conversation_id, triage_data)

    async def get(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Recupera uma triagem associada a uma conversa.

        Args:
            conversation_id (str): Identificador da conversa.

        Returns:
            Optional[Dict[str, Any]]: Documento da triagem, se existir.
        """
        return await self.persistence.get_triage(conversation_id)
