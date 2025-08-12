import logging
import os

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

def get_env_variable(name, default=None, required=True):
    value = os.getenv(name, default)
    if required and not value:
        raise EnvironmentError(f"Variabile d'ambiente mancante: {name}")
    return value
