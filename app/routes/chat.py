from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])
def get_chat_service() -> ChatService:
    return ChatService()

@router.post("/", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_endpoint(
    payload: ChatRequest,
    service: ChatService = Depends(get_chat_service)
):
    """
    Endpoint de interação com o agente de triagem.

    Este endpoint recebe uma mensagem de um usuário, processa o conteúdo
    utilizando o serviço de chat e retorna a resposta do agente.

    - **Request body**: ChatRequest (inclui identificador da conversa,
      mensagem do usuário, canal e identificador do usuário).
    - **Response body**: ChatResponse (contendo identificador da conversa,
      mensagem de resposta do agente e timestamp).
    - **Erros possíveis**:
        - 500: Erro interno no processamento da mensagem.
    """
    try:
        return await service.process_message(payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno no processamento da mensagem: {str(e)}"
        )
