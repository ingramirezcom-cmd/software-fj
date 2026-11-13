"""Clase base para las entidades del sistema."""
from abc import ABC, abstractmethod

from sistema.excepciones import ParametroFaltanteError


class EntidadBase(ABC):
    """Base común de los objetos que tienen un identificador.

    No se crea directamente: cada clase concreta define su propio resumen.
    """

    def __init__(self, identificador):
        if identificador is None or not str(identificador).strip():
            raise ParametroFaltanteError("el identificador es obligatorio")
        self._identificador = str(identificador).strip().upper()

    @property
    def identificador(self) -> str:
        """Devuelve el identificador, que no se puede cambiar."""
        return self._identificador

    @abstractmethod
    def resumen(self) -> str:
        """Devuelve un resumen breve de la entidad."""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._identificador})"
