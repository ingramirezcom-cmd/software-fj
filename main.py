"""Punto de inicio de la aplicación.

Ejecuta ejemplos de clientes, servicios y reservas. Si alguno falla, el sistema
lo registra y continúa con el siguiente.
"""
from sistema.gestor import GestorSistema
from sistema.registro import ARCHIVO_LOG, obtener_logger


# Cada ejemplo recibe el gestor; algunos muestran errores esperados del sistema.

def caso_cliente_valido(g):
    return g.registrar_cliente({
        "id": "C001", "nombre": "Ana Martínez", "documento": "1020304050",
        "email": "ana@correo.com", "telefono": "3001234567",
    })


def caso_cliente_email_invalido(g):
    return g.registrar_cliente({
        "id": "C002", "nombre": "Luis Pérez", "documento": "80123456", "email": "luis.correo",
    })


def caso_cliente_sin_documento(g):
    return g.registrar_cliente({"id": "C003", "nombre": "Marta Ruiz", "email": "marta@correo.com"})


def caso_cliente_nombre_con_numeros(g):
    return g.registrar_cliente({
        "id": "C004", "nombre": "Pedro 3", "documento": "70111222", "email": "pedro@correo.com",
    })


def caso_cliente_duplicado(g):
    return g.registrar_cliente({
        "id": "C001", "nombre": "Ana Otra", "documento": "99887766", "email": "otra@correo.com",
    })


def caso_sala_valida(g):
    return g.crear_servicio("sala", {
        "identificador": "S001", "nombre": "Sala Júpiter", "tarifa_hora": 50000, "capacidad": 10,
    })


def caso_equipo_tarifa_negativa(g):
    return g.crear_servicio("equipo", {
        "identificador": "S002", "nombre": "Proyector 4K", "tarifa_hora": -100,
        "tipo_equipo": "Proyector", "unidades": 2,
    })


def caso_servicio_tipo_desconocido(g):
    return g.crear_servicio("auto", {"identificador": "S099", "nombre": "Carro", "tarifa_hora": 1000})


def caso_asesoria_valida(g):
    return g.crear_servicio("asesoria", {
        "identificador": "S003", "nombre": "Seguridad Informática", "tarifa_hora": 80000,
        "especialidad": "Ciberseguridad",
    })


def caso_equipo_sin_unidades(g):
    return g.crear_servicio("equipo", {
        "identificador": "S004", "nombre": "Portátil", "tarifa_hora": 20000,
        "tipo_equipo": "Portátil",
    })


def caso_equipo_valido(g):
    return g.crear_servicio("equipo", {
        "identificador": "S005", "nombre": "Portátil Pro", "tarifa_hora": 20000,
        "tipo_equipo": "Portátil", "unidades": 2,
    })


def caso_reserva_exitosa(g):
    g.crear_reserva("R001", "C001", "S001", 3)
    g.confirmar_reserva("R001")
    return g.procesar_reserva("R001", impuesto=0.19, descuento=0.05)


def caso_reserva_cliente_inexistente(g):
    return g.crear_reserva("R002", "C999", "S001", 2)


def caso_reserva_horas_excesivas(g):
    return g.crear_reserva("R003", "C001", "S001", 30)


def caso_reserva_servicio_no_disponible(g):
    g.cambiar_disponibilidad("S003", False)
    try:
        g.crear_reserva("R004", "C001", "S003", 2)
        return g.confirmar_reserva("R004")
    finally:
        g.cambiar_disponibilidad("S003", True)  # Se vuelve a habilitar para los siguientes ejemplos.


def caso_procesar_sin_confirmar(g):
    g.crear_reserva("R005", "C001", "S001", 1)
    return g.procesar_reserva("R005")


def caso_cancelar_reserva_procesada(g):
    return g.cancelar_reserva("R001")  # Esta reserva ya se procesó en el ejemplo anterior.


def caso_calculo_inconsistente(g):
    g.crear_reserva("R006", "C001", "S005", 2)
    g.confirmar_reserva("R006")
    return g.procesar_reserva("R006", impuesto=0.19, descuento=1.5)  # El descuento supera el 100 %.


def caso_cancelar_reserva_pendiente(g):
    g.crear_reserva("R007", "C001", "S003", 4)
    return g.cancelar_reserva("R007", motivo="el cliente cambió de fecha")


def caso_error_no_previsto(g):
    # Comprueba que un error inesperado no interrumpa los demás ejemplos.
    return 1 / 0


def caso_reporte_ingresos(g):
    return g.reporte_ingresos()


ESCENARIOS = [
    ("Cliente válido", caso_cliente_valido),
    ("Cliente con email inválido", caso_cliente_email_invalido),
    ("Cliente sin documento (parámetro faltante)", caso_cliente_sin_documento),
    ("Cliente con nombre con números", caso_cliente_nombre_con_numeros),
    ("Cliente duplicado", caso_cliente_duplicado),
    ("Servicio sala válido", caso_sala_valida),
    ("Servicio equipo con tarifa negativa", caso_equipo_tarifa_negativa),
    ("Servicio de tipo desconocido", caso_servicio_tipo_desconocido),
    ("Servicio asesoría válido", caso_asesoria_valida),
    ("Servicio equipo sin unidades", caso_equipo_sin_unidades),
    ("Servicio equipo válido", caso_equipo_valido),
    ("Reserva exitosa (crear, confirmar, procesar)", caso_reserva_exitosa),
    ("Reserva con cliente inexistente", caso_reserva_cliente_inexistente),
    ("Reserva con duración excesiva", caso_reserva_horas_excesivas),
    ("Reserva con servicio no disponible", caso_reserva_servicio_no_disponible),
    ("Procesar reserva sin confirmar", caso_procesar_sin_confirmar),
    ("Cancelar reserva ya procesada", caso_cancelar_reserva_procesada),
    ("Cálculo inconsistente (descuento 150 %)", caso_calculo_inconsistente),
    ("Cancelar reserva pendiente", caso_cancelar_reserva_pendiente),
    ("Error no previsto (división por cero)", caso_error_no_previsto),
    ("Reporte de ingresos", caso_reporte_ingresos),
]


def main() -> int:
    obtener_logger().info("===== Inicio de la simulación de Software FJ =====")
    gestor = GestorSistema()
    exitosos = 0
    controlados = 0

    print("=" * 78)
    print("SOFTWARE FJ - Simulación de operaciones")
    print("=" * 78)
    for numero, (titulo, caso) in enumerate(ESCENARIOS, start=1):
        ok, valor = gestor.ejecutar_seguro(f"{numero:02d} {titulo}", caso, gestor)
        if ok:
            exitosos += 1
            print(f"{numero:02d}. {titulo:<46} OK  -> {valor}")
        else:
            controlados += 1
            etiqueta = "ERROR NO PREVISTO" if str(valor).startswith("error no previsto") else "FALLO CONTROLADO"
            print(f"{numero:02d}. {titulo:<46} {etiqueta}")
            print(f"      motivo: {valor}")

    print("-" * 78)
    print(f"Operaciones: {len(ESCENARIOS)} | exitosas: {exitosos} | "
          f"con error controlado: {controlados}")
    print(f"Estado final del sistema: {gestor.resumen_sistema()}")
    print(f"Registro de eventos y errores: {ARCHIVO_LOG}")
    print("=" * 78)
    obtener_logger().info("===== Fin de la simulación: %d exitosas, %d con error =====",
                          exitosos, controlados)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
