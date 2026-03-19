import logging

def setup_logging() -> None:
    """Configura o logging da aplicação."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    )
