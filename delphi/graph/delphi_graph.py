# delphi/graph/delphi_graph.py

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
    deuda_total: Decimal       # capturado — reservado para sprint futuro
    cuota_mensual: Decimal
    sector: str
    escenarios: Optional[EscenariosResult]
    veredicto: str
    recomendaciones: list[str]
    error: Optional[str]


def initial_state(mensaje: str) -> DelphiState:
    """Construye el estado inicial del grafo con valores por defecto seguros.

    Todos los campos numéricos comienzan en Decimal('0') — nunca float.
    escenarios y error comienzan en None; se populan en sus nodos respectivos.
    """
    return DelphiState(
        mensaje_usuario=mensaje,
        historial=[],
        ingresos_mensuales=Decimal("0"),
        gastos_mensuales=Decimal("0"),
        deuda_total=Decimal("0"),
        cuota_mensual=Decimal("0"),
        sector="",
        escenarios=None,
        veredicto="",
        recomendaciones=[],
        error=None,
    )


def build_graph():
    """Ensambla y compila el StateGraph de Delphi.

    Arquitectura de tres nodos en secuencia:
      intake → scenario → advisor

    Los agentes se importan aquí para evitar importaciones circulares
    y permitir que DelphiState e initial_state sean importables de forma
    independiente sin necesitar las dependencias de cada agente.
    """
    from delphi.agents.intake_agent import intake_node
    from delphi.agents.scenario_agent import scenario_node
    from delphi.agents.advisor_agent import advisor_node

    builder = StateGraph(DelphiState)

    builder.add_node("intake", intake_node)
    builder.add_node("scenario", scenario_node)
    builder.add_node("advisor", advisor_node)

    builder.set_entry_point("intake")
    builder.add_edge("intake", "scenario")
    builder.add_edge("scenario", "advisor")
    builder.set_finish_point("advisor")

    return builder.compile()
