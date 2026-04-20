# delphi/tests/test_delphi_graph.py

import pytest
from decimal import Decimal

from delphi.graph.delphi_graph import DelphiState, initial_state, build_graph


# ---------------------------------------------------------------------------
# DelphiState — estructura del TypedDict
# ---------------------------------------------------------------------------


class TestDelphiState:
    CAMPOS_REQUERIDOS = {
        "mensaje_usuario",
        "historial",
        "ingresos_mensuales",
        "gastos_mensuales",
        "deuda_total",
        "cuota_mensual",
        "sector",
        "fecha_corte",
        "escenarios",
        "veredicto",
        "recomendaciones",
        "sesion_id",
        "error",
        "error_persistencia",
    }

    def test_initial_state_tiene_todos_los_campos(self):
        """initial_state devuelve un dict con exactamente los campos del State."""
        state = initial_state("necesito un crédito")
        assert set(state.keys()) == self.CAMPOS_REQUERIDOS

    def test_initial_state_guarda_mensaje_usuario(self):
        """El mensaje del usuario se persiste intacto en el State."""
        msg = "quiero saber si puedo pagar un crédito de 50 millones"
        state = initial_state(msg)
        assert state["mensaje_usuario"] == msg

    def test_initial_state_campos_financieros_son_decimal_cero(self):
        """Decisión #5: campos numéricos comienzan en Decimal('0'), nunca float."""
        state = initial_state("test")
        for campo in ("ingresos_mensuales", "gastos_mensuales", "deuda_total", "cuota_mensual"):
            assert state[campo] == Decimal("0"), f"{campo} debe ser Decimal('0')"
            assert isinstance(state[campo], Decimal), f"{campo} debe ser Decimal, no {type(state[campo])}"

    def test_initial_state_listas_vacias(self):
        """historial y recomendaciones comienzan como listas vacías."""
        state = initial_state("test")
        assert state["historial"] == []
        assert state["recomendaciones"] == []
        assert isinstance(state["historial"], list)
        assert isinstance(state["recomendaciones"], list)

    def test_initial_state_error_es_none(self):
        """error comienza en None — sin errores antes de correr ningún nodo."""
        state = initial_state("test")
        assert state["error"] is None

    def test_initial_state_escenarios_es_none(self):
        """Decisión #6: escenarios comienza en None antes de correr scenario_node."""
        state = initial_state("test")
        assert state["escenarios"] is None

    def test_initial_state_sector_y_veredicto_vacios(self):
        state = initial_state("test")
        assert state["sector"] == ""
        assert state["veredicto"] == ""

    def test_initial_state_campos_nuevos_son_none(self):
        """fecha_corte, sesion_id y error_persistencia comienzan en None."""
        state = initial_state("test")
        assert state["fecha_corte"] is None
        assert state["sesion_id"] is None
        assert state["error_persistencia"] is None


# ---------------------------------------------------------------------------
# build_graph — ensamblaje del StateGraph
# ---------------------------------------------------------------------------


class TestBuildGraph:
    def test_build_graph_retorna_grafo_compilado(self):
        """build_graph() devuelve un grafo compilado invocable."""
        from langgraph.graph.state import CompiledStateGraph
        grafo = build_graph()
        assert isinstance(grafo, CompiledStateGraph)

    def test_build_graph_tiene_los_cuatro_nodos(self):
        """El grafo contiene los cuatro nodos del pipeline."""
        grafo = build_graph()
        nodos = set(grafo.nodes.keys())
        assert "intake" in nodos
        assert "scenario" in nodos
        assert "advisor" in nodos
        assert "persistence" in nodos
