"""Datos y validaciones de los clientes."""
import re

from sistema.entidades import EntidadBase
from sistema.excepciones import ParametroFaltanteError, ValidacionError

PATRON_EMAIL = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")


def _validar_nombre(nombre) -> str:
    if nombre is None or (isinstance(nombre, str) and not nombre.strip()):
        raise ParametroFaltanteError("el nombre es obligatorio")
    if not isinstance(nombre, str):
        raise ValidacionError("el nombre debe ser texto")
    limpio = nombre.strip()
    # Se aceptan letras con tilde y espacios, pero no números ni símbolos.
    if len(limpio) < 3 or not all(c.isalpha() or c.isspace() for c in limpio):
        raise ValidacionError("el nombre debe tener al menos 3 letras y no contener números")
    return limpio.title()


def _validar_documento(documento) -> str:
    if documento is None or not str(documento).strip():
        raise ParametroFaltanteError("el documento es obligatorio")
    texto = str(documento).strip()
    if not texto.isdigit() or not 6 <= len(texto) <= 12:
        raise ValidacionError("el documento debe tener entre 6 y 12 dígitos")
    return texto


def _validar_email(email) -> str:
    if email is None or not str(email).strip():
        raise ParametroFaltanteError("el correo electrónico es obligatorio")
    correo = str(email).strip().lower()
    if not PATRON_EMAIL.match(correo):
        raise ValidacionError(f"el correo '{correo}' no tiene un formato válido")
    return correo


def _validar_telefono(telefono) -> str:
    if telefono is None or not str(telefono).strip():
        return ""  # El teléfono no es obligatorio.
    texto = str(telefono).strip().replace(" ", "")
    if texto.startswith("+"):
        texto = texto[1:]
    if not texto.isdigit() or not 7 <= len(texto) <= 15:
        raise ValidacionError("el teléfono debe tener entre 7 y 15 dígitos")
    return texto


class Cliente(EntidadBase):
    """Representa a un cliente y protege sus datos con validaciones."""

    def __init__(self, identificador, nombre, documento, email, telefono=""):
        super().__init__(identificador)
        try:
            self._nombre = _validar_nombre(nombre)
            self._documento = _validar_documento(documento)
            self._email = _validar_email(email)
            self._telefono = _validar_telefono(telefono)
        except ValidacionError as error:
            # Conserva el error original para poder consultar qué falló.
            raise type(error)(
                f"cliente {self.identificador} inválido: {error.mensaje}"
            ) from error

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def documento(self) -> str:
        return self._documento

    @property
    def email(self) -> str:
        return self._email

    @property
    def telefono(self) -> str:
        return self._telefono

    def actualizar_contacto(self, email=None, telefono=None) -> None:
        """Actualiza el correo y el teléfono solo si ambos datos son válidos."""
        nuevo_email = _validar_email(email) if email is not None else self._email
        nuevo_telefono = (
            _validar_telefono(telefono) if telefono is not None else self._telefono
        )
        self._email = nuevo_email
        self._telefono = nuevo_telefono

    def resumen(self) -> str:
        return f"Cliente {self.identificador}: {self._nombre} | doc {self._documento} | {self._email}"
