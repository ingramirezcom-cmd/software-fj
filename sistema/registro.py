"""Registro de los eventos y errores del sistema.

Los datos de clientes, servicios y reservas se mantienen en memoria; este
archivo solo guarda el registro de lo que ocurre.
"""
import logging
import os
import sys

DIRECTORIO_LOGS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs"
)
ARCHIVO_LOG = os.path.join(DIRECTORIO_LOGS, "eventos_y_errores.log")
NOMBRE_LOGGER = "software_fj"


def obtener_logger() -> logging.Logger:
    """Prepara el registro la primera vez y devuelve el logger."""
    logger = logging.getLogger(NOMBRE_LOGGER)
    if logger.handlers:
        return logger

    formato = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    try:
        os.makedirs(DIRECTORIO_LOGS, exist_ok=True)
        manejador = logging.FileHandler(ARCHIVO_LOG, encoding="utf-8")
        origen = ARCHIVO_LOG
    except OSError as error:
        # Si no se puede abrir el archivo, mostramos el registro en la consola.
        manejador = logging.StreamHandler(sys.stderr)
        origen = f"consola (no se pudo abrir el archivo: {error})"

    manejador.setFormatter(formato)
    logger.addHandler(manejador)
    logger.info("Registro iniciado en: %s", origen)
    return logger
