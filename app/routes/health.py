from fastapi import APIRouter, status
from datetime import datetime

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", status_code=status.HTTP_200_OK)
async def healthcheck() -> dict:
    """
    Endpoint de verificação de saúde da aplicação.

    Retorna um objeto simples com status e timestamp,
    permitindo que sistemas de monitoramento validem
    se a API está operacional.
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
