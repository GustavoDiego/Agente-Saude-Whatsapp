from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class ChatRequest(BaseModel):
    """
    Representa a requisição enviada ao agente de triagem.

    Esta estrutura encapsula os dados mínimos necessários
    para processar uma mensagem de usuário em um chat.
    """

    conversation_id: str = Field(
        ...,
        description="Identificador único da conversa (ex.: número de telefone hasheado ou UUID gerado)."
    )
    user_id: Optional[str] = Field(
        None,
        description="Identificador do usuário no canal de origem (ex.: wa_id, hash)."
    )
    channel: Literal["whatsapp", "web"] = Field(
        ...,
        description="Origem da mensagem."
    )
    message: str = Field(
        ...,
        description="Conteúdo textual enviado pelo usuário."
    )


class ChatResponse(BaseModel):
    """
    Representa a resposta retornada pelo agente.

    Inclui a mensagem do agente, além de dados
    para rastreamento de sessão e auditoria.
    """

    conversation_id: str = Field(
        ...,
        description="Identificador único da conversa."
    )
    response: str = Field(
        ...,
        description="Mensagem gerada pelo agente."
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Carimbo de tempo UTC da resposta."
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
