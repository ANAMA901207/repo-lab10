# delphi/graph/delphi_graph.py

from datetime import date
from decimal import Decimal
from typing import Optional

from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

from delphi.skills.financial_calc import EscenariosResult


class DelphiState(TypedDict):
    mensaje_usuario: str
    historial: list[dict]
    ingresos_mensuales: Decimal
    gastos_mensuales: Decimal
    deuda_total: Decimal           # capturado — reservado para sprint futuro
    cuota_mensual: Decimal
    sector: str
    fecha_corte: Optional[date]    # extraída por intake; default = hoy (Bogotá)
    escenarios: Optional[EscenariosResult]
    veredicto: str
    recomendaciones: list[str]
    sesion_id: Optional[str]       # UUID devuelto por Supabase tras crear sesión
    error: Optional[str]
    error_persistencia: Optional[str]  # errores de BD; no interrumpe el flujo


def initial_state(mensaje: str) -> DelphiState:
    """Construye el estado inicial del grafo con valores por defecto seguros.

    Todos los campos numéricos comienzan en Decimal('0') — nunca float.
    fecha_corte, sesion_id y errores comienzan en None.
    """
    return DelphiState(
        mensaje_usuario=mensaje,
        historial=[],
        ingresos_mensuales=Decimal("0"),
        gastos_mensuales=Decimal("0"),
        deuda_total=Decimal("0"),
        cuota_mensual=Decimal("0"),
        sector="",
        fecha_corte=None,
        escenarios=None,
        veredicto="",
        recomendaciones=[],
        sesion_id=None,
        error=None,
        error_persistencia=None,
    )


def build_graph():
    """Ensambla y compila el StateGraph de Delphi.

    Arquitectura de cuatro nodos en secuencia:
      intake → scenario → advisor → persistence

    Los agentes se importan aquí para evitar importaciones circulares
    y permitir que DelphiState e initial_state sean importables de forma
    independiente sin necesitar las dependencias de cada agente.
    """
    from delphi.agents.intake_agent import intake_node
    from delphi.agents.scenario_agent import scenario_node
    from delphi.agents.advisor_agent import advisor_node
    from delphi.agents.persistence_agent import persistence_node

    builder = StateGraph(DelphiState)

    builder.add_node("intake", intake_node)
    builder.add_node("scenario", scenario_node)
    builder.add_node("advisor", advisor_node)
    builder.add_node("persistence", persistence_node)

    builder.set_entry_point("intake")
    builder.add_edge("intake", "scenario")
    builder.add_edge("scenario", "advisor")
    builder.add_edge("advisor", "persistence")
    builder.set_finish_point("persistence")

    return builder.compile()
