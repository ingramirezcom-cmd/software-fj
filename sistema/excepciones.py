"""Errores propios del sistema.

Al compartir una clase base, el gestor puede reconocer los errores esperados
sin confundirlos con fallos inesperados.
"""


class SoftwareFJError(Exception):
    """Error general del sistema."""

    codigo = "ERR_GENERAL"

    def __init__(self, mensaje: str):
        super().__init__(mensaje)
        self.mensaje = mensaje

    def __str__(self) -> str:
        return f"[{self.codigo}] {self.mensaje}"


class ValidacionError(SoftwareFJError):
    """Se recibió un dato con formato, tipo o valor no válido."""

    codigo = "ERR_VALIDACION"


class ParametroFaltanteError(ValidacionError):
    """Falta un dato necesario para completar la operación."""

    codigo = "ERR_PARAMETRO_FALTANTE"


class OperacionNoPermitidaError(SoftwareFJError):
    """La operación no se puede realizar en el estado actual."""

    codigo = "ERR_OPERACION_NO_PERMITIDA"


class EntidadNoEncontradaError(SoftwareFJError):
    """No se encontró el cliente, servicio o reserva solicitado."""

    codigo = "ERR_NO_ENCONTRADO"


class ServicioNoDisponibleError(SoftwareFJError):
    """El servicio está registrado, pero no está disponible."""

    codigo = "ERR_SERVICIO_NO_DISPONIBLE"


class CalculoError(SoftwareFJError):
    """El cálculo produjo un resultado no válido."""

    codigo = "ERR_CALCULO"


class ReservaError(SoftwareFJError):
    """No se pudo completar una operación de reserva."""

    codigo = "ERR_RESERVA"
