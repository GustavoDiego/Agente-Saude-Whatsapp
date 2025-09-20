"""
Configurações globais da aplicação.
Carregadas a partir de variáveis de ambiente ou do arquivo `.env`.
"""

from pydantic_settings import BaseSettings
from pydantic import Field

from functools import lru_cache


class Settings(BaseSettings):
    """Configurações principais da aplicação."""

    APP_NAME: str = Field("ClinicAI WhatsApp Agent", description="Nome da aplicação")
    APP_HOST: str = Field("0.0.0.0", description="Host do servidor FastAPI")
    APP_PORT: int = Field(8000, description="Porta do servidor FastAPI")
    ENV: str = Field("dev", description="Ambiente de execução (dev/staging/prod)")


    MONGO_URI: str = Field("mongodb://localhost:27017", description="URI de conexão do MongoDB")
    MONGO_DB: str = Field("clinicai", description="Nome do banco de dados MongoDB")


    WHATSAPP_PHONE_NUMBER_ID: str = Field(..., description="Phone Number ID do WhatsApp")
    WHATSAPP_VERIFY_TOKEN: str = Field(..., description="Token de verificação do Webhook")
    WHATSAPP_ACCESS_TOKEN: str = Field(..., description="Access Token da API do WhatsApp")


    GOOGLE_API_KEY: str = Field(..., description="Chave de API para o Gemini")


    APP_SECRET: str = Field(..., description="Segredo usado para criptografia ou JWT")
    HASH_SALT: str = Field(..., description="Salt para hash de identificadores de usuário")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    """Retorna instância única das configurações carregadas."""
    return Settings()



settings = get_settings()
