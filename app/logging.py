import logging
from app.config import Config

def setup_logging():
    """
    Configura il logging globale dell'applicazione.
    Se l'ambiente è 'dev', imposta il livello DEBUG, altrimenti INFO.
    Il formato include timestamp, livello, nome logger e messaggio.

    Returns:
        None
    """
    # Determina il livello di logging in base all'ambiente
    level = logging.DEBUG if Config.ENV == "dev" else logging.INFO

    # Configura il logging di base con formato e data personalizzati
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)