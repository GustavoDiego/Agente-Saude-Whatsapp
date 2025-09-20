from typing import Optional, List, Dict
from pydantic import BaseModel, Field, root_validator


class WhatsAppProfile(BaseModel):
    """Perfil associado a um contato do WhatsApp."""
    name: Optional[str] = None


class WhatsAppContact(BaseModel):
    """Contato que interage com o bot via WhatsApp."""
    wa_id: str
    profile: Optional[WhatsAppProfile] = None


class WhatsAppText(BaseModel):
    """Mensagem de texto recebida ou enviada."""
    body: str


class WhatsAppMessage(BaseModel):
    """Estrutura de mensagem recebida no webhook do WhatsApp."""
    id: str
    from_: str = Field(..., alias="from")
    timestamp: str
    type: str
    text: Optional[WhatsAppText] = None


class WhatsAppChangeValue(BaseModel):
    """Valor detalhado de uma mudança no webhook."""
    messaging_product: str
    metadata: Dict[str, str]
    contacts: Optional[List[WhatsAppContact]] = None
    messages: Optional[List[WhatsAppMessage]] = None


class WhatsAppChange(BaseModel):
    """Mudança (event) recebida no webhook."""
    field: str
    value: WhatsAppChangeValue


class WhatsAppEntry(BaseModel):
    """Entrada de evento no webhook."""
    id: str
    changes: List[WhatsAppChange]


class WhatsAppWebhookPayload(BaseModel):
    """Payload completo do webhook do WhatsApp."""
    object: str
    entry: List[WhatsAppEntry]


class WhatsAppSendMessage(BaseModel):
    """
    Estrutura para envio de mensagens ao WhatsApp.
    Usada pelo cliente WhatsAppService.
    """
    messaging_product: str = Field("whatsapp", const=True)
    to: str
    type: str = Field("text", const=True)
    text: WhatsAppText

    @root_validator
    def ensure_text_when_type_text(cls, values):
        """Valida que mensagens de texto contenham corpo obrigatório."""
        if values.get("type") == "text" and not values.get("text"):
            raise ValueError("Mensagens de texto precisam de campo 'text.body'")
        return values
