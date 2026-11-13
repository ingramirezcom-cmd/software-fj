"""Reservas y sus cambios de estado."""
from sistema.cliente import Cliente
from sistema.entidades import EntidadBase
from sistema.excepciones import (
    OperacionNoPermitidaError,
    ReservaError,
    ServicioNoDisponibleError,
    SoftwareFJError,
    ValidacionError,
)
from sistema.registro import obtener_logger
from sistema.servicios import Servicio

PENDIENTE = "PENDIENTE"
CONFIRMADA = "CONFIRMADA"
CANCELADA = "CANCELADA"
PROCESADA = "PROCESADA"


class Reserva(EntidadBase):
    """Une un cliente con un servicio y controla el estado de la reserva."""

    def __init__(self, identificador, cliente, servicio, horas):
        super().__init__(identificador)
        if not isinstance(cliente, Cliente):
            raise ValidacionError(f"la reserva {self.identificador} requiere un Cliente válido")
        if not isinstance(servicio, Servicio):
            raise ValidacionError(f"la reserva {self.identificador} requiere un Servicio válido")
        try:
            servicio.validar_parametros(horas)
        except SoftwareFJError as error:
            raise ReservaError(
                f"reserva {self.identificador} rechazada: {error.mensaje}"
            ) from error

        self._cliente = cliente
        self._servicio = servicio
        self._horas = float(horas)  # El servicio ya comprobó que la duración sea válida.
        self._estado = PENDIENTE
        self._costo_total = None
        obtener_logger().info(
            "Reserva %s creada: cliente %s, servicio %s, %.1f h",
            self.identificador, cliente.identificador, servicio.identificador, self._horas,
        )

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def horas(self) -> float:
        return self._horas

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def costo_total(self):
        return self._costo_total

    def confirmar(self) -> None:
        if self._estado != PENDIENTE:
            raise OperacionNoPermitidaError(
                f"no se puede confirmar la reserva {self.identificador} en estado {self._estado}"
            )
        try:
            self._servicio.verificar_disponibilidad()
        except ServicioNoDisponibleError as error:
            obtener_logger().warning("Reserva %s no confirmada: %s", self.identificador, error)
            raise ReservaError(
                f"no se puede confirmar la reserva {self.identificador}"
            ) from error
        self._estado = CONFIRMADA
        obtener_logger().info("Reserva %s confirmada", self.identificador)

    def cancelar(self, motivo: str = "sin motivo indicado") -> None:
        if self._estado in (CANCELADA, PROCESADA):
            raise OperacionNoPermitidaError(
                f"la reserva {self.identificador} no se puede cancelar: estado {self._estado}"
            )
        self._estado = CANCELADA
        obtener_logger().info("Reserva %s cancelada (%s)", self.identificador, motivo)

    def procesar(self, impuesto=None, descuento=None) -> float:
        """Calcula el costo final de una reserva confirmada."""
        if self._estado != CONFIRMADA:
            raise OperacionNoPermitidaError(
                f"solo se procesan reservas confirmadas; {self.identificador} está {self._estado}"
            )
        registro = obtener_logger()
        try:
            costo = self._servicio.calcular_costo(
                self._horas, impuesto=impuesto, descuento=descuento
            )
        except SoftwareFJError as error:
            registro.error("Reserva %s no procesada: %s", self.identificador, error)
            raise ReservaError(
                f"no se pudo procesar la reserva {self.identificador}"
            ) from error
        else:
            self._costo_total = costo
            self._estado = PROCESADA
            registro.info("Reserva %s procesada, costo total %.2f", self.identificador, costo)
            return costo
        finally:
            registro.debug("Fin del procesamiento de %s (estado %s)", self.identificador, self._estado)

    def resumen(self) -> str:
        return (
            f"Reserva {self.identificador}: {self._cliente.nombre} | "
            f"{self._servicio.nombre} | {self._horas:.1f} h | {self._estado}"
        )
