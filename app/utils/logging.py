import sys
from loguru import logger


def configure_logging():
    """
    Configura o logger global da aplicação.

    - Saída no stdout (console).
    - Formato padronizado com nível, horário e mensagem.
    - Rotação automática de arquivos de log.
    """
    logger.remove()


    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        level="DEBUG",
    )

    logger.add(
        "logs/clinicai.log",
        rotation="10 MB",
        retention="10 days",
        compression="zip",
        encoding="utf-8",
        enqueue=True,
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    )

    logger.info("Logger configurado com sucesso.")



configure_logging()
