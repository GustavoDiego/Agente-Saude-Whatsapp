"""
Schemas Pydantic para armazenar informações estruturadas da triagem.
Este schema também pode ser usado para gerar o JSON Schema automaticamente
para guiar o LLM na extração.
"""

from pydantic import BaseModel, Field, conint
from typing import Optional

IntensityScale = conint(ge=0, le=10)


class Triage(BaseModel):
    """Estrutura consolidada da triagem coletada pelo agente."""

    conversation_id: Optional[str] = Field(
        None, description="Identificador único da conversa associada."
    )
    queixa_principal: str = Field(
        default="", description="Motivo central do contato."
    )
    sintomas: str = Field(
        default="", description="Descrição detalhada dos sintomas."
    )
    duracao_frequencia: str = Field(
        default="", description="Desde quando os sintomas começaram e com que frequência ocorrem."
    )
    intensidade: IntensityScale = Field(
        default=0, description="Intensidade da dor/desconforto (escala de 0 a 10)."
    )
    historico: str = Field(
        default="", description="Condições pré-existentes ou episódios anteriores."
    )
    medidas_tomadas: str = Field(
        default="", description="Medidas adotadas pelo usuário até agora."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                "queixa_principal": "Dor no peito",
                "sintomas": "Dor contínua no lado esquerdo do peito, irradiando para o braço.",
                "duracao_frequencia": "Começou há 2 dias, ocorre várias vezes ao dia.",
                "intensidade": 8,
                "historico": "Hipertensão, episódio semelhante há 1 ano.",
                "medidas_tomadas": "Tomou analgésico, sem melhora.",
            }
        }
