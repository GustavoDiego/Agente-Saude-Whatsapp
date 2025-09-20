import httpx
from app.schemas.whatsapp import WhatsAppSendMessage
from app.settings import settings


class WhatsAppService:
    """
    Cliente para envio de mensagens via WhatsApp Cloud API.

    Este serviço abstrai a comunicação com a API da Meta, permitindo
    o envio de mensagens estruturadas no formato definido pelo schema
    `WhatsAppSendMessage`.
    """

    def __init__(self) -> None:
        self.base_url = "https://graph.facebook.com/v22.0"
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN

        if not self.phone_number_id or not self.access_token:
            raise ValueError(
                "Configuração do WhatsApp incompleta: "
                "verifique WHATSAPP_PHONE_NUMBER_ID e WHATSAPP_ACCESS_TOKEN."
            )

    async def send_message(self, payload: WhatsAppSendMessage) -> dict:
        """
        Envia uma mensagem de texto para um usuário no WhatsApp.

        Args:
            payload (WhatsAppSendMessage): Estrutura contendo o número do destinatário
                                           e o conteúdo da mensagem.

        Returns:
            dict: Resposta JSON da API do WhatsApp.

        Raises:
            httpx.HTTPStatusError: Caso a API retorne erro HTTP.
        """
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, headers=headers, json=payload.dict())
            response.raise_for_status()
            return response.json()
