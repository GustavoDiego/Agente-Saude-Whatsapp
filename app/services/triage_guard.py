"""
Serviço para identificar possíveis emergências nas mensagens recebidas.
Baseado nas constantes definidas em app/constants/emergencies.py.
"""

from app.constants.emergencies import EMERGENCY_KEYWORDS, EMERGENCY_MESSAGE


class TriageGuard:
    """
    Serviço responsável por detectar situações de emergência em mensagens.
    Utiliza palavras-chave pré-definidas em `EMERGENCY_KEYWORDS`.
    """

    def __init__(self) -> None:
        self.keywords = [kw.lower() for kw in EMERGENCY_KEYWORDS]
        self.alert_message = EMERGENCY_MESSAGE

    def is_emergency(self, user_message: str) -> bool:
        """
        Verifica se a mensagem contém indícios de emergência.

        Args:
            user_message (str): Texto enviado pelo usuário.

        Returns:
            bool: True se for detectada emergência, False caso contrário.
        """
        lower_text = user_message.lower()
        return any(keyword in lower_text for keyword in self.keywords)

    def get_alert_message(self) -> str:
        """
        Retorna a mensagem padrão a ser enviada em caso de emergência.

        Returns:
            str: Mensagem de alerta pré-definida.
        """
        return self.alert_message
