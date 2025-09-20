from datetime import datetime
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm import LLMClient
from app.services.persistence import PersistenceService
from app.services.triage_guard import TriageGuard


class ChatService:
    """
    Serviço responsável pelo processamento das mensagens de chat.

    Este serviço coordena as seguintes etapas:
    1. Persistência da mensagem recebida do usuário.
    2. Detecção de gatilhos de emergência na mensagem.
    3. Encaminhamento do conteúdo à LLM para gerar resposta.
    4. Persistência da resposta do agente.
    5. Retorno da resposta ao cliente chamador.

    Dependências externas:
    - LLMClient: responsável por gerar respostas com base em prompts.
    - PersistenceService: responsável por salvar e recuperar mensagens/sessões.
    - TriageGuard: responsável por detectar situações de emergência.
    """

    def __init__(
        self,
        llm_client: LLMClient = LLMClient(),
        persistence: PersistenceService = PersistenceService(),
        guard: TriageGuard = TriageGuard(),
    ):
        self.llm_client = llm_client
        self.persistence = persistence
        self.guard = guard

    async def process_message(self, payload: ChatRequest) -> ChatResponse:
        """
        Processa uma mensagem recebida do usuário.

        Fluxo:
        - Armazena a mensagem do usuário na base de dados.
        - Avalia se o conteúdo contém gatilhos de emergência.
        - Caso não haja emergência, envia a mensagem para a LLM gerar uma resposta.
        - Armazena a resposta gerada na base de dados.
        - Retorna a resposta em formato estruturado.

        Args:
            payload (ChatRequest): Dados da mensagem recebida.

        Returns:
            ChatResponse: Resposta estruturada do agente.
        """
        await self.persistence.save_message(
            conversation_id=payload.conversation_id,
            sender="user",
            content=payload.message,
            channel=payload.channel,
            user_id=payload.user_id,
        )

        if self.guard.is_emergency(payload.message):
            response_text = (
                "Entendi. Seus sintomas podem indicar uma situação de emergência. "
                "Por favor, procure o pronto-socorro mais próximo ou ligue para o 192 imediatamente."
            )
        else:

            response_text = await self.llm_client.generate_response(
                conversation_id=payload.conversation_id,
                message=payload.message,
                user_id=payload.user_id,
            )

        await self.persistence.save_message(
            conversation_id=payload.conversation_id,
            sender="agent",
            content=response_text,
            channel=payload.channel,
            user_id=payload.user_id,
        )


        return ChatResponse(
            conversation_id=payload.conversation_id,
            response=response_text,
            timestamp=datetime.utcnow(),
        )
