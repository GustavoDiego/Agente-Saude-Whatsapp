import uvicorn
from fastapi import FastAPI
from app.routes import chat
from app.routes import health
from fastapi.middleware.cors import CORSMiddleware

def create_app() -> FastAPI:
    """
    Cria e configura a aplicação FastAPI.

    Retorna:
        FastAPI: Instância configurada da aplicação.
    """
    app = FastAPI(
        title="ClinicAI - Agente de Triagem",
        description=(
            "Assistente virtual para coleta inicial de informações clínicas. "
            "O agente é acolhedor, ético e não substitui avaliação médica."
        ),
        version="1.0.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],   
        allow_credentials=True,
        allow_methods=["*"],  
        allow_headers=["*"],   
    )

  
    app.include_router(health.router)
    app.include_router(chat.router)

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
