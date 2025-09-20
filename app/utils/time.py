from datetime import datetime, timezone


def now_utc() -> datetime:
    """
    Retorna o horário atual em UTC.

    Returns:
        datetime: Objeto datetime com timezone UTC.
    """
    return datetime.now(timezone.utc)


def format_iso(dt: datetime) -> str:
    """
    Formata um datetime no padrão ISO 8601 com sufixo Z.

    Args:
        dt (datetime): Objeto datetime a ser formatado.

    Returns:
        str: Data/hora formatada em ISO 8601 (UTC).
    """
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_iso(iso_str: str) -> datetime:
    """
    Converte uma string ISO 8601 em objeto datetime UTC.

    Args:
        iso_str (str): Data/hora no formato ISO 8601.

    Returns:
        datetime: Objeto datetime com timezone UTC.
    """
    return datetime.fromisoformat(iso_str.replace("Z", "+00:00")).astimezone(timezone.utc)
