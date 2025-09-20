from fastapi import APIRouter, Request, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from app.schemas.whatsapp import WhatsAppWebhookPayload, WhatsAppSendMessage
from app.services.whatsapp import WhatsAppService
from app.services.triage_guard import TriageGuard
from app.services.llm import LLMService
from app.services.persistence import PersistenceService
from app.settings import settings
import hashlib

router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.get("/whatsapp")
async def verify_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
):
    """
    Endpoint GET para verificação do webhook com o Meta.

    O Meta envia `hub.mode`, `hub.challenge` e `hub.verify_token`.
    Este endpoint compara o token recebido com o token configurado
    no ambiente da aplicação. Se forem iguais, devolve o challenge
    de volta, confirmando a assinatura do webhook.
    """
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Token inválido para verificação.")


@router.post("/whatsapp")
async def receive_webhook(payload: WhatsAppWebhookPayload, request: Request):
    """
    Endpoint POST para recepção de mensagens do WhatsApp.

    Fluxo:
    1. Recebe payload no formato `WhatsAppWebhookPayload`.
    2. Extrai mensagem e número do usuário.
    3. Aplica guard de triagem (detecção de emergências).
    4. Encaminha para o LLM para condução da triagem.
    5. Salva conversa no banco de dados.
    6. Responde ao usuário via WhatsApp API.

    Regras:
    - Nunca gera diagnóstico ou tratamento.
    - Interrompe triagem em caso de emergência e orienta procurar ajuda imediata.
    """
    whatsapp_service = WhatsAppService()
    llm_service = LLMService()
    persistence = PersistenceService()
    guard = TriageGuard()

    try:

        change = payload.entry[0].changes[0].value
        msg = change.messages[0]
        user_number = msg.from_
        user_text = msg.text.body if msg.text else ""

        phone_hash = hashlib.sha256(
            f"{user_number}{settings.HASH_SALT}".encode()
        ).hexdigest()

        if guard.is_emergency(user_text):
            emergency_reply = (
                "Entendi. Seus sintomas podem indicar uma situação de emergência. "
                "Por favor, procure o pronto-socorro mais próximo ou ligue 192 imediatamente."
            )
            await whatsapp_service.send_message(
                WhatsAppSendMessage(to=user_number, text={"body": emergency_reply})
            )
            persistence.save_message(phone_hash, user_text, emergency_reply)
            return JSONResponse(content={"status": "emergency_handled"})

       
        agent_reply = await llm_service.get_reply(user_text, session_id=phone_hash)

       
        persistence.save_message(phone_hash, user_text, agent_reply)

   
        await whatsapp_service.send_message(
            WhatsAppSendMessage(to=user_number, text={"body": agent_reply})
        )

        return JSONResponse(content={"status": "ok"})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")
