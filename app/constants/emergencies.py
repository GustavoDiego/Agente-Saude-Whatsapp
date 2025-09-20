"""
Constantes relacionadas à detecção de emergências médicas.

Este módulo centraliza a lista de palavras-chave que indicam
potenciais situações de emergência, bem como a mensagem padrão
que deve ser enviada ao usuário nesses casos.
"""


EMERGENCY_KEYWORDS = [
    "dor no peito",
    "falta de ar",
    "desmaio",
    "sangramento intenso",
    "confusão mental",
    "convulsão",
    "inconsciência",
    "pressão muito alta",
    "pressão muito baixa",
    "fraqueza súbita",
    "dificuldade para falar",
    "dificuldade para andar",
    "perda de visão súbita",
]

EMERGENCY_MESSAGE = (
    "Entendi. Seus sintomas podem indicar uma situação de emergência. "
    "Por favor, procure o pronto-socorro mais próximo ou ligue para o 192 imediatamente."
)
