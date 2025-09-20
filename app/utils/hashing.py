import os
import hashlib
import hmac


class Hasher:
    """
    Serviço utilitário para hashing seguro de identificadores sensíveis.

    Utiliza HMAC-SHA256 com salt para garantir integridade e
    evitar exposição direta de dados como números de telefone.
    """

    def __init__(self, salt: str = None):
        """
        Inicializa o Hasher com um salt definido por ambiente.

        Args:
            salt (str): String usada como salt. Se não fornecida,
                        será lida da variável de ambiente HASH_SALT.
        """
        self.salt = (salt or os.getenv("HASH_SALT", "default_salt")).encode("utf-8")

    def hash_value(self, value: str) -> str:
        """
        Gera o hash seguro de um valor.

        Args:
            value (str): Texto a ser hasheado.

        Returns:
            str: Representação hexadecimal do hash.
        """
        return hmac.new(self.salt, value.encode("utf-8"), hashlib.sha256).hexdigest()

    def verify_value(self, value: str, hashed: str) -> bool:
        """
        Verifica se um valor corresponde ao hash armazenado.

        Args:
            value (str): Valor original.
            hashed (str): Hash previamente gerado.

        Returns:
            bool: True se o valor corresponder ao hash.
        """
        return hmac.compare_digest(self.hash_value(value), hashed)
