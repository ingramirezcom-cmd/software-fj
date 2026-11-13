# Software FJ – Sistema integral de gestión de clientes, servicios y reservas

Proyecto del Ejercicio 1 (Anexo 3, Fase 4) del curso Programación 213023.
Aplicación orientada a objetos en Python, **sin base de datos**: la información vive en
objetos y listas; los archivos solo se usan para el registro de eventos y errores.

## Requisitos

- Python 3.9 o superior (probado con Python 3.13). No requiere librerías externas.

## Cómo ejecutar

```bash
python main.py          # simulación de 21 operaciones (válidas e inválidas)
python -m unittest -v   # pruebas automatizadas (18 pruebas)
```

Los errores y eventos se escriben en `logs/eventos_y_errores.log`.

## Estructura

| Archivo | Contenido |
|---|---|
| `main.py` | Simulación de operaciones; cada una se ejecuta de forma segura. |
| `sistema/excepciones.py` | Jerarquía de excepciones personalizadas (`SoftwareFJError` y derivadas). |
| `sistema/registro.py` | Configuración del log (con plan B a consola si no se puede escribir el archivo). |
| `sistema/entidades.py` | **Clase abstracta** `EntidadBase` (identificador único, método abstracto `resumen`). |
| `sistema/cliente.py` | Clase `Cliente`: datos personales encapsulados y validados. |
| `sistema/servicios.py` | **Clase abstracta** `Servicio` y tres especializaciones: `SalaReunion`, `AlquilerEquipo`, `AsesoriaEspecializada`. |
| `sistema/reserva.py` | Clase `Reserva`: cliente, servicio, duración y estado; confirmar, cancelar y procesar. |
| `sistema/gestor.py` | `GestorSistema`: listas internas, coordinación y red de seguridad (`ejecutar_seguro`). |
| `tests/test_sistema.py` | Pruebas unitarias. |

## Conceptos de POO aplicados

- **Abstracción:** `EntidadBase` y `Servicio` son clases abstractas (`ABC`); no se pueden instanciar.
- **Herencia:** `Cliente`, `Reserva` y los servicios heredan de sus bases.
- **Polimorfismo:** `costo_base`, `validar_parametros` y `describir` se sobrescriben en cada servicio; `calcular_costo` devuelve resultados distintos según el tipo.
- **Encapsulación:** atributos privados (`_nombre`, `_email`…) con propiedades de solo lectura; los cambios pasan por métodos que validan primero (`actualizar_contacto` es atómico).
- **Sobrecarga:** Python no tiene sobrecarga nativa, así que `calcular_costo` se emula con parámetros opcionales: `(horas)`, `(horas, impuesto)` y `(horas, impuesto, descuento)`.

## Manejo de excepciones

- **Jerarquía propia:** `ValidacionError`, `ParametroFaltanteError`, `OperacionNoPermitidaError`, `EntidadNoEncontradaError`, `ServicioNoDisponibleError`, `CalculoError`, `ReservaError`.
- **Bloques:** `try/except`, `try/except/else` (en `Reserva.procesar`) y `try/except/finally` (en `Reserva.procesar` y `GestorSistema.ejecutar_seguro`).
- **Encadenamiento:** se usa `raise ... from error` para conservar la causa original (por ejemplo, `ReservaError` conserva el `ServicioNoDisponibleError` que la originó).
- **Estabilidad:** `ejecutar_seguro` captura tanto los errores controlados como los no previstos (con traza completa en el log), de modo que el programa sigue ejecutándose.

## Estado de una reserva

```
PENDIENTE --confirmar--> CONFIRMADA --procesar--> PROCESADA
    |                        |
    +------cancelar----------+--> CANCELADA
```


Curso de Programación (213023) - Fase 4, Componente práctico - UNAD

Una reserva procesada no se puede cancelar, y una que no está confirmada no se puede procesar.

## Integrantes del equipo
- Eladio Ramírez Sánchez
- Rubiney Diaz Martinez
