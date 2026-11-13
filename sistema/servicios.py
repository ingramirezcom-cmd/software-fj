"""Servicios disponibles y sus reglas de cálculo.

Cada tipo de servicio valida sus propias condiciones y calcula su costo.
"""
import math
from abc import ABC, abstractmethod

from sistema.entidades import EntidadBase
from sistema.excepciones import (
    CalculoError,
    ParametroFaltanteError,
    ServicioNoDisponibleError,
    ValidacionError,
)

HORAS_MAXIMAS = 12
CARGO_LIMPIEZA = 15000.0


def validar_horas(horas, maximo=HORAS_MAXIMAS) -> float:
    """Comprueba que la duración esté dentro del límite permitido."""
    if horas is None:
        raise ParametroFaltanteError("la duración en horas es obligatoria")
    if isinstance(horas, bool) or not isinstance(horas, (int, float)):
        raise ValidacionError(f"la duración '{horas}' debe ser numérica")
    if not math.isfinite(horas) or not 0 < horas <= maximo:
        raise ValidacionError(f"la duración debe estar entre 0 y {maximo} horas")
    return float(horas)


def _validar_entero(valor, nombre, minimo, maximo) -> int:
    if valor is None:
        raise ParametroFaltanteError(f"{nombre} es obligatorio")
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise ValidacionError(f"{nombre} debe ser un número entero")
    if not minimo <= valor <= maximo:
        raise ValidacionError(f"{nombre} debe estar entre {minimo} y {maximo}")
    return valor


def _validar_texto(valor, nombre) -> str:
    if valor is None or not str(valor).strip():
        raise ParametroFaltanteError(f"{nombre} es obligatorio")
    return str(valor).strip()


class Servicio(EntidadBase, ABC):
    """Define los datos y las operaciones comunes de los servicios."""

    def __init__(self, identificador, nombre, tarifa_hora, disponible=True):
        super().__init__(identificador)
        self._nombre = _validar_texto(nombre, "el nombre del servicio")
        self._tarifa_hora = self._validar_tarifa(tarifa_hora)
        self._disponible = bool(disponible)

    @staticmethod
    def _validar_tarifa(tarifa) -> float:
        if tarifa is None:
            raise ParametroFaltanteError("la tarifa por hora es obligatoria")
        try:
            valor = float(tarifa)
        except (TypeError, ValueError) as error:
            raise ValidacionError(f"la tarifa '{tarifa}' no es numérica") from error
        if not math.isfinite(valor) or valor <= 0:
            raise ValidacionError("la tarifa debe ser un número positivo")
        return valor

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def tarifa_hora(self) -> float:
        return self._tarifa_hora

    @property
    def disponible(self) -> bool:
        return self._disponible

    def cambiar_disponibilidad(self, disponible: bool) -> None:
        self._disponible = bool(disponible)

    def verificar_disponibilidad(self) -> None:
        if not self._disponible:
            raise ServicioNoDisponibleError(
                f"el servicio {self._nombre} no está disponible en este momento"
            )

    @abstractmethod
    def validar_parametros(self, horas) -> None:
        """Comprueba las reglas de duración propias de cada servicio."""

    @abstractmethod
    def costo_base(self, horas) -> float:
        """Calcula el costo antes de aplicar impuestos o descuentos."""

    @abstractmethod
    def describir(self) -> str:
        """Devuelve una descripción del servicio."""

    def resumen(self) -> str:
        return f"Servicio {self.identificador}: {self.describir()}"

    def calcular_costo(self, horas, impuesto=None, descuento=None) -> float:
        """Calcula el costo base y, si se indican, aplica impuesto y descuento.

        Los parámetros opcionales permiten usar el método con solo las horas,
        con horas e impuesto, o con los tres valores.
        """
        self.validar_parametros(horas)
        base = self.costo_base(horas)
        return self.ajustar_costo(base, impuesto, descuento)

    @staticmethod
    def ajustar_costo(base, impuesto=None, descuento=None) -> float:
        """Aplica impuesto y descuento después de comprobar sus valores."""
        try:
            tasa = 0.0 if impuesto is None else float(impuesto)
            rebaja = 0.0 if descuento is None else float(descuento)
        except (TypeError, ValueError) as error:
            raise CalculoError("el impuesto o el descuento no son numéricos") from error

        if not 0 <= tasa <= 1 or not 0 <= rebaja < 1:
            raise CalculoError(
                f"valores fuera de rango: impuesto={tasa}, descuento={rebaja}"
            )
        total = base * (1 - rebaja) * (1 + tasa)
        if not math.isfinite(total) or total <= 0:
            raise CalculoError("el cálculo produjo un valor inconsistente")
        return round(total, 2)


class SalaReunion(Servicio):
    """Servicio de sala con cobro por hora y cargo de limpieza."""

    def __init__(self, identificador, nombre, tarifa_hora, capacidad, disponible=True):
        super().__init__(identificador, nombre, tarifa_hora, disponible)
        self._capacidad = _validar_entero(capacidad, "la capacidad", 1, 200)

    @property
    def capacidad(self) -> int:
        return self._capacidad

    def validar_parametros(self, horas) -> None:
        validar_horas(horas)

    def costo_base(self, horas) -> float:
        return self.tarifa_hora * validar_horas(horas) + CARGO_LIMPIEZA

    def describir(self) -> str:
        return (
            f"Sala de reuniones '{self.nombre}' para {self._capacidad} personas, "
            f"${self.tarifa_hora:,.0f}/h + limpieza"
        )


class AlquilerEquipo(Servicio):
    """Servicio de alquiler de equipos por hora y cantidad de unidades."""

    def __init__(self, identificador, nombre, tarifa_hora, tipo_equipo, unidades,
                 disponible=True):
        super().__init__(identificador, nombre, tarifa_hora, disponible)
        self._tipo_equipo = _validar_texto(tipo_equipo, "el tipo de equipo")
        self._unidades = _validar_entero(unidades, "las unidades", 1, 50)

    @property
    def unidades(self) -> int:
        return self._unidades

    def validar_parametros(self, horas) -> None:
        validar_horas(horas)

    def costo_base(self, horas) -> float:
        return self.tarifa_hora * validar_horas(horas) * self._unidades

    def describir(self) -> str:
        return (
            f"Alquiler de {self._unidades} x {self._tipo_equipo} ('{self.nombre}'), "
            f"${self.tarifa_hora:,.0f}/h por unidad"
        )


class AsesoriaEspecializada(Servicio):
    """Asesoría con un límite de horas y un recargo para sesiones largas."""

    HORAS_MAXIMAS_ASESORIA = 8
    HORAS_RECARGO = 4
    RECARGO_SENIOR = 0.10

    def __init__(self, identificador, nombre, tarifa_hora, especialidad, disponible=True):
        super().__init__(identificador, nombre, tarifa_hora, disponible)
        self._especialidad = _validar_texto(especialidad, "la especialidad")

    def validar_parametros(self, horas) -> None:
        validar_horas(horas, maximo=self.HORAS_MAXIMAS_ASESORIA)

    def costo_base(self, horas) -> float:
        duracion = validar_horas(horas, maximo=self.HORAS_MAXIMAS_ASESORIA)
        base = self.tarifa_hora * duracion
        if duracion > self.HORAS_RECARGO:
            base *= 1 + self.RECARGO_SENIOR
        return base

    def describir(self) -> str:
        return (
            f"Asesoría especializada en {self._especialidad} ('{self.nombre}'), "
            f"${self.tarifa_hora:,.0f}/h"
        )
