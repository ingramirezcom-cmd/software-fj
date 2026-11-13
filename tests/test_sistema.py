"""Pruebas de las operaciones principales del sistema."""
import unittest

from sistema.cliente import Cliente
from sistema.excepciones import (
    CalculoError,
    OperacionNoPermitidaError,
    ParametroFaltanteError,
    ReservaError,
    ServicioNoDisponibleError,
    ValidacionError,
)
from sistema.gestor import GestorSistema
from sistema.reserva import CANCELADA, CONFIRMADA, PROCESADA, Reserva
from sistema.servicios import AsesoriaEspecializada, SalaReunion, Servicio


class TestCliente(unittest.TestCase):
    def test_cliente_valido(self):
        cliente = Cliente("c1", "ana lópez", "1020304050", "ANA@correo.com")
        self.assertEqual(cliente.identificador, "C1")
        self.assertEqual(cliente.nombre, "Ana López")
        self.assertEqual(cliente.email, "ana@correo.com")

    def test_email_invalido_lanza_validacion_con_causa(self):
        with self.assertRaises(ValidacionError) as contexto:
            Cliente("c2", "Luis Pérez", "80123456", "luis.correo")
        # El mensaje permite comprobar que se detectó el formato incorrecto.
        self.assertIn("correo", contexto.exception.mensaje)

    def test_documento_faltante_es_parametro_faltante(self):
        with self.assertRaises(ParametroFaltanteError):
            Cliente("c3", "Marta Ruiz", None, "marta@correo.com")

    def test_actualizacion_atomica_no_cambia_nada_si_falla(self):
        cliente = Cliente("c4", "Pedro Gómez", "70111222", "pedro@correo.com", "3001234567")
        with self.assertRaises(ValidacionError):
            cliente.actualizar_contacto(email="correo-malo", telefono="3009999999")
        self.assertEqual(cliente.email, "pedro@correo.com")
        self.assertEqual(cliente.telefono, "3001234567")


class TestServicios(unittest.TestCase):
    def test_servicio_abstracto_no_se_instancia(self):
        with self.assertRaises(TypeError):
            Servicio("X", "Algo", 1000)

    def test_tarifa_negativa_rechazada(self):
        with self.assertRaises(ValidacionError):
            SalaReunion("S1", "Sala", -5, 10)

    def test_polimorfismo_costos_distintos(self):
        sala = SalaReunion("S1", "Sala", 50000, 10)
        asesoria = AsesoriaEspecializada("S2", "Asesor", 80000, "Redes")
        # La sala cobra las horas reservadas y un cargo de limpieza.
        self.assertEqual(sala.calcular_costo(2), 115000.0)
        # Las asesorías de más de cuatro horas tienen un recargo del 10 %.
        self.assertEqual(asesoria.calcular_costo(5), 440000.0)

    def test_sobrecarga_emulada_con_impuesto_y_descuento(self):
        sala = SalaReunion("S1", "Sala", 50000, 10)
        self.assertEqual(sala.calcular_costo(3), 165000.0)
        self.assertEqual(sala.calcular_costo(3, 0.19), 196350.0)
        self.assertEqual(sala.calcular_costo(3, 0.19, 0.10), 176715.0)

    def test_descuento_fuera_de_rango_es_error_de_calculo(self):
        sala = SalaReunion("S1", "Sala", 50000, 10)
        with self.assertRaises(CalculoError):
            sala.calcular_costo(2, 0.19, 1.5)


class TestReserva(unittest.TestCase):
    def setUp(self):
        self.cliente = Cliente("c1", "Ana López", "1020304050", "ana@correo.com")
        self.sala = SalaReunion("S1", "Sala", 50000, 10)

    def test_ciclo_completo(self):
        reserva = Reserva("R1", self.cliente, self.sala, 3)
        reserva.confirmar()
        self.assertEqual(reserva.estado, CONFIRMADA)
        costo = reserva.procesar(impuesto=0.19)
        self.assertEqual(costo, 196350.0)
        self.assertEqual(reserva.estado, PROCESADA)

    def test_no_se_procesa_sin_confirmar(self):
        reserva = Reserva("R2", self.cliente, self.sala, 1)
        with self.assertRaises(OperacionNoPermitidaError):
            reserva.procesar()

    def test_no_se_cancela_una_procesada(self):
        reserva = Reserva("R3", self.cliente, self.sala, 1)
        reserva.confirmar()
        reserva.procesar()
        with self.assertRaises(OperacionNoPermitidaError):
            reserva.cancelar()

    def test_cancelar_pendiente(self):
        reserva = Reserva("R4", self.cliente, self.sala, 1)
        reserva.cancelar("prueba")
        self.assertEqual(reserva.estado, CANCELADA)

    def test_servicio_deshabilitado_impide_confirmar(self):
        self.sala.cambiar_disponibilidad(False)
        reserva = Reserva("R5", self.cliente, self.sala, 1)
        with self.assertRaises(ReservaError) as contexto:
            reserva.confirmar()
        self.assertIsInstance(contexto.exception.__cause__, ServicioNoDisponibleError)

    def test_reserva_con_duracion_excesiva(self):
        with self.assertRaises(ReservaError):
            Reserva("R6", self.cliente, self.sala, 99)


class TestGestor(unittest.TestCase):
    def test_gestor_sobrevive_a_error_no_previsto(self):
        gestor = GestorSistema()
        ok, mensaje = gestor.ejecutar_seguro("prueba", lambda: 1 / 0)
        self.assertFalse(ok)
        self.assertIn("ZeroDivisionError", mensaje)

    def test_reporte_sin_reservas_es_error_controlado(self):
        gestor = GestorSistema()
        with self.assertRaises(CalculoError):
            gestor.reporte_ingresos()

    def test_id_duplicado_rechazado(self):
        gestor = GestorSistema()
        datos = {"id": "C1", "nombre": "Ana López", "documento": "1020304050",
                 "email": "ana@correo.com"}
        gestor.registrar_cliente(datos)
        with self.assertRaises(OperacionNoPermitidaError):
            gestor.registrar_cliente(datos)


if __name__ == "__main__":
    unittest.main()
