# delphi/agents/scenario_agent.py

from delphi.graph.delphi_graph import DelphiState
from delphi.skills.financial_calc import calcular_escenarios


def scenario_node(state: DelphiState) -> DelphiState:
    """Calcula los tres escenarios financieros del usuario.

    Workflow puro — no llama al LLM. Lee los datos del State y delega
    todo el cálculo a calcular_escenarios() de financial_calc.py.

    Decisión #2: si state['error'] no es None, retorna inmediatamente
    sin ejecutar para que el error del nodo anterior se propague.

    Args:
        state: Estado del grafo con ingresos_mensuales, gastos_mensuales
               y cuota_mensual ya poblados por intake_node.

    Returns:
        Estado actualizado con 'escenarios' (EscenariosResult) o con
        'error' si algo falla en el cálculo.
    """
    if state["error"] is not None:
        return state

    try:
        escenarios = calcular_escenarios(
            ingresos=state["ingresos_mensuales"],
            gastos=state["gastos_mensuales"],
            cuota=state["cuota_mensual"],
        )
        return {**state, "escenarios": escenarios, "error": None}

    except Exception as e:
        return {**state, "error": f"scenario_node: {e}"}
