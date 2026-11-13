"""Coordina las operaciones con clientes, servicios y reservas."""
from sistema.cliente import Cliente
from sistema.excepciones import (
    CalculoError,
    EntidadNoEncontradaError,
    OperacionNoPermitidaError,
    ParametroFaltanteError,
    SoftwareFJError,
    ValidacionError,
)
from sistema.registro import obtener_logger
from sistema.reserva import PROCESADA, Reserva
from sistema.servicios import AlquilerEquipo, AsesoriaEspecializada, SalaReunion


class GestorSistema:
    """Administra los datos del sistema mientras la aplicación está en uso."""

    FABRICA_SERVICIOS = {
        "sala": SalaReunion,
        "equipo": AlquilerEquipo,
        "asesoria": AsesoriaEspecializada,
    }

    def __init__(self):
        self._clientes = []
        self._servicios = []
        self._reservas = []
        self._log = obtener_logger()

    # Métodos auxiliares
    @staticmethod
    def _normalizar(identificador) -> str:
        if identificador is None or not str(identificador).strip():
            raise ParametroFaltanteError("se requiere un identificador")
        return str(identificador).strip().upper()

    def _buscar(self, lista, identificador, tipo):
        clave = self._normalizar(identificador)
        for elemento in lista:
            if elemento.identificador == clave:
                return elemento
        raise EntidadNoEncontradaError(f"no existe el {tipo} '{clave}'")

    def _existe(self, lista, identificador) -> bool:
        clave = self._normalizar(identificador)
        return any(elemento.identificador == clave for elemento in lista)

    @staticmethod
    def _exigir_dict(datos, nombre):
        if not isinstance(datos, dict):
            raise ValidacionError(f"los datos de {nombre} deben entregarse como diccionario")

    # Gestión de clientes
    def registrar_cliente(self, datos: dict) -> Cliente:
        self._exigir_dict(datos, "el cliente")
        try:
            cliente = Cliente(
                datos["id"],
                datos["nombre"],
                datos["documento"],
                datos["email"],
                datos.get("telefono", ""),
            )
        except KeyError as error:
            raise ParametroFaltanteError(f"falta el campo obligatorio {error}") from error

        if self._existe(self._clientes, cliente.identificador):
            raise OperacionNoPermitidaError(
                f"ya existe un cliente con id {cliente.identificador}"
            )
        self._clientes.append(cliente)
        self._log.info("Cliente %s registrado", cliente.identificador)
        return cliente

    # Gestión de servicios
    def crear_servicio(self, tipo: str, datos: dict):
        clase = self.FABRICA_SERVICIOS.get(str(tipo).strip().lower())
        if clase is None:
            raise ValidacionError(
                f"tipo de servicio desconocido '{tipo}'; use: {', '.join(self.FABRICA_SERVICIOS)}"
            )
        self._exigir_dict(datos, "el servicio")
        try:
            servicio = clase(**datos)
        except TypeError as error:
            raise ParametroFaltanteError(
                f"parámetros incompletos o inválidos para '{tipo}': {error}"
            ) from error

        if self._existe(self._servicios, servicio.identificador):
            raise OperacionNoPermitidaError(
                f"ya existe un servicio con id {servicio.identificador}"
            )
        self._servicios.append(servicio)
        self._log.info("Servicio %s creado (%s)", servicio.identificador, tipo)
        return servicio

    def cambiar_disponibilidad(self, id_servicio, disponible: bool):
        servicio = self._buscar(self._servicios, id_servicio, "servicio")
        servicio.cambiar_disponibilidad(disponible)
        self._log.info("Servicio %s disponible=%s", servicio.identificador, disponible)
        return servicio

    # Gestión de reservas
    def crear_reserva(self, identificador, id_cliente, id_servicio, horas) -> Reserva:
        cliente = self._buscar(self._clientes, id_cliente, "cliente")
        servicio = self._buscar(self._servicios, id_servicio, "servicio")
        if self._existe(self._reservas, identificador):
            raise OperacionNoPermitidaError(f"ya existe una reserva con id {identificador}")
        reserva = Reserva(identificador, cliente, servicio, horas)
        self._reservas.append(reserva)
        return reserva

    def confirmar_reserva(self, identificador) -> Reserva:
        reserva = self._buscar(self._reservas, identificador, "reserva")
        reserva.confirmar()
        return reserva

    def cancelar_reserva(self, identificador, motivo="sin motivo indicado") -> Reserva:
        reserva = self._buscar(self._reservas, identificador, "reserva")
        reserva.cancelar(motivo)
        return reserva

    def procesar_reserva(self, identificador, impuesto=None, descuento=None) -> float:
        reserva = self._buscar(self._reservas, identificador, "reserva")
        return reserva.procesar(impuesto=impuesto, descuento=descuento)

    # Reportes del sistema
    def reporte_ingresos(self) -> float:
        procesadas = [r for r in self._reservas if r.estado == PROCESADA]
        if not procesadas:
            raise CalculoError("no hay reservas procesadas para calcular ingresos")
        total = round(sum(r.costo_total for r in procesadas), 2)
        self._log.info("Reporte de ingresos: %d reservas, total %.2f", len(procesadas), total)
        return total

    def resumen_sistema(self) -> str:
        return (
            f"clientes={len(self._clientes)}, servicios={len(self._servicios)}, "
            f"reservas={len(self._reservas)}"
        )

    # Ejecución segura de operaciones
    def ejecutar_seguro(self, descripcion, funcion, *args, **kwargs):
        """Ejecuta una operación y devuelve su resultado o el mensaje del error.

        Los errores esperados quedan como advertencias; los inesperados se guardan
        con su detalle para poder revisarlos.
        """
        try:
            resultado = funcion(*args, **kwargs)
        except SoftwareFJError as error:
            self._log.warning("[%s] Error controlado: %s", descripcion, error)
            return False, str(error)
        except Exception as error:  # Registra los errores inesperados sin detener el sistema.
            self._log.exception("[%s] Error NO previsto: %r", descripcion, error)
            return False, f"error no previsto: {type(error).__name__}: {error}"
        else:
            self._log.info("[%s] Operación exitosa", descripcion)
            return True, resultado
