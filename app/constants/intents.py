"""
Constantes de intenções simples para classificar mensagens do usuário.

Essas intenções podem ser utilizadas pelo agente para ajustar
o tom da conversa, controlar o fluxo ou registrar métricas.
"""

INTENTS = {
    "GREETING": ["olá", "oi", "boa tarde", "bom dia", "boa noite", "salve"],
    "FAREWELL": ["tchau", "até logo", "até mais", "adeus", "falou", "obrigado"],
    "AFFIRMATION": ["sim", "claro", "com certeza", "positivo"],
    "NEGATION": ["não", "negativo", "nunca"],
    "THANKS": ["valeu", "obrigado", "obrigada", "agradecido"],
    "HELP": ["ajuda", "socorro", "preciso de ajuda"],
    "TRIAGE": [
        "dor",
        "sintoma",
        "estou sentindo",
        "estou com",
        "me sinto",
        "tenho",
    ],
}
