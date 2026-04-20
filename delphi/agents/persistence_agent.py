# delphi/agents/persistence_agent.py

import os
from pathlib import Path

from dotenv import load_dotenv

import delphi.db as db
from delphi.graph.delphi_graph import DelphiState

_ENV_PATH = Path(__file__).parent.parent / ".env"


def _get_supabase_client() -> object:
    """Crea y retorna un Supabase SyncClient usando credenciales del .env."""
    load_dotenv(_ENV_PATH)
    from supabase import create_client
    return create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_KEY"],
    )


def _formatear_respuesta_delphi(state: DelphiState) -> str:
    """Construye el texto de respuesta de Delphi para guardar en 'mensajes'."""
    veredicto = state["veredicto"].upper()
    recomendaciones = "\n".join(
        f"{i + 1}. {r}" for i, r in enumerate(state["recomendaciones"])
    )
    return f"Veredicto: {veredicto}\n\nRecomendaciones:\n{recomendaciones}"


def persistence_node(state: DelphiState) -> DelphiState:
    """Persiste la sesión completa en Supabase.

    Flujo:
      1. Si state['error'] no es None → retorna sin ejecutar.
      2. Crea sesión en 'sesiones' (usuario_id='anonimo', sector extraído).
      3. Guarda datos financieros en 'datos_financieros' (incluye fecha_corte).
      4. Guarda resultados DSCR y veredicto en 'resultados'.
      5. Guarda mensaje del usuario + respuesta de Delphi en 'mensajes'.
      6. Actualiza estado de la sesión a 'completado'.

    Si crear_sesion falla, los pasos 3-6 se abortan (decisión #4).
    Cualquier excepción se escribe en error_persistencia; state['error'] no se toca.

    Args:
        state: Estado completo del grafo tras pasar por advisor_node.

    Returns:
        Estado actualizado con sesion_id y error_persistencia.
    """
    if state["error"] is not None:
        return state

    cliente = _get_supabase_client()

    try:
        sesion_id = db.crear_sesion(cliente, "anonimo", state["sector"])
    except Exception as exc:
        return {**state, "error_persistencia": f"persistence_node: {exc}"}

    try:
        db.guardar_datos_financieros(
            cliente,
            sesion_id=sesion_id,
            ingresos_mensuales=state["ingresos_mensuales"],
            gastos_mensuales=state["gastos_mensuales"],
            deuda_total=state["deuda_total"],
            cuota_mensual=state["cuota_mensual"],
            fecha_corte=state["fecha_corte"],
        )

        escenarios = state["escenarios"]
        db.guardar_resultados(
            cliente,
            sesion_id=sesion_id,
            dscr_base=escenarios["base"]["dscr"],
            dscr_optimista=escenarios["optimista"]["dscr"],
            dscr_pesimista=escenarios["pesimista"]["dscr"],
            veredicto=state["veredicto"],
            recomendaciones=state["recomendaciones"],
        )

        respuesta_delphi = _formatear_respuesta_delphi(state)
        db.guardar_mensajes(
            cliente,
            sesion_id=sesion_id,
            mensaje_usuario=state["mensaje_usuario"],
            respuesta_delphi=respuesta_delphi,
        )

        db.completar_sesion(cliente, sesion_id)

        return {**state, "sesion_id": sesion_id, "error_persistencia": None}

    except Exception as exc:
        return {**state, "sesion_id": sesion_id, "error_persistencia": f"persistence_node: {exc}"}
