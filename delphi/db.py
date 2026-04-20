# delphi/db.py

from datetime import date
from decimal import Decimal
from typing import Optional


def crear_sesion(cliente: object, usuario_id: str, sector: str) -> str:
    """Inserta una nueva fila en 'sesiones' y retorna el UUID generado.

    Args:
        cliente: Supabase SyncClient autenticado.
        usuario_id: Identificador del usuario (e.g. "anonimo").
        sector: Sector económico extraído del mensaje.

    Returns:
        UUID de la sesión recién creada.
    """
    respuesta = (
        cliente.table("sesiones")  # type: ignore[attr-defined]
        .insert({"usuario_id": usuario_id, "sector": sector})
        .execute()
    )
    return respuesta.data[0]["id"]


def guardar_datos_financieros(
    cliente: object,
    sesion_id: str,
    ingresos_mensuales: Decimal,
    gastos_mensuales: Decimal,
    deuda_total: Decimal,
    cuota_mensual: Decimal,
    fecha_corte: Optional[date],
) -> None:
    """Inserta los datos financieros en 'datos_financieros'.

    Los Decimal se convierten a float (Supabase NUMERIC).
    fecha_corte se serializa como ISO 8601 string o None.
    """
    cliente.table("datos_financieros").insert(  # type: ignore[attr-defined]
        {
            "sesion_id": sesion_id,
            "ingresos_mensuales": float(ingresos_mensuales),
            "gastos_mensuales": float(gastos_mensuales),
            "deuda_total": float(deuda_total),
            "cuota_mensual": float(cuota_mensual),
            "fecha_corte": fecha_corte.isoformat() if fecha_corte is not None else None,
        }
    ).execute()


def guardar_resultados(
    cliente: object,
    sesion_id: str,
    dscr_base: Decimal,
    dscr_optimista: Decimal,
    dscr_pesimista: Decimal,
    veredicto: str,
    recomendaciones: list[str],
) -> None:
    """Inserta los resultados DSCR y el veredicto en 'resultados'.

    Los DSCR Decimal se convierten a float.
    recomendaciones se envía como lista (JSONB).
    """
    cliente.table("resultados").insert(  # type: ignore[attr-defined]
        {
            "sesion_id": sesion_id,
            "dscr_base": float(dscr_base),
            "dscr_optimista": float(dscr_optimista),
            "dscr_pesimista": float(dscr_pesimista),
            "veredicto": veredicto,
            "recomendaciones": recomendaciones,
        }
    ).execute()


def guardar_mensajes(
    cliente: object,
    sesion_id: str,
    mensaje_usuario: str,
    respuesta_delphi: str,
) -> None:
    """Inserta el mensaje del usuario y la respuesta de Delphi en 'mensajes'."""
    cliente.table("mensajes").insert(  # type: ignore[attr-defined]
        [
            {"sesion_id": sesion_id, "rol": "usuario", "contenido": mensaje_usuario},
            {"sesion_id": sesion_id, "rol": "asistente", "contenido": respuesta_delphi},
        ]
    ).execute()


def completar_sesion(cliente: object, sesion_id: str) -> None:
    """Actualiza el campo 'estado' de la sesión a 'completado'."""
    (
        cliente.table("sesiones")  # type: ignore[attr-defined]
        .update({"estado": "completado"})
        .eq("id", sesion_id)
        .execute()
    )
