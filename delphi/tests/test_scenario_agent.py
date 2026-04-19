# delphi/tests/test_scenario_agent.py

import pytest
from decimal import Decimal

from delphi.graph.delphi_graph import initial_state
from delphi.agents.scenario_agent import scenario_node
from delphi.skills.financial_calc import EscenariosResult


def _state_valido(**kwargs):
    """Estado base con datos financieros de una PyME normal."""
    state = initial_state("quiero un crédito")
    state.update({
        "ingresos_mensuales": Decimal("10000000"),
        "gastos_mensuales": Decimal("7000000"),
        "cuota_mensual": Decimal("2000000"),
        "sector": "comercio",
    })
    state.update(kwargs)
    return state


class TestScenarioNode:
    def test_caso_feliz_calcula_escenarios(self):
        """scenario_node popula state['escenarios'] con EscenariosResult."""
        resultado = scenario_node(_state_valido())
        assert resultado["escenarios"] is not None
        assert resultado["error"] is None

    def test_escenarios_tiene_tres_claves(self):
        """EscenariosResult incluye base, optimista y pesimista."""
        resultado = scenario_node(_state_valido())
        escenarios = resultado["escenarios"]
        assert "base" in escenarios
        assert "optimista" in escenarios
        assert "pesimista" in escenarios

    def test_escenario_base_dscr_correcto(self):
        """base DSCR = (10M - 7M) / 2M = 1.50."""
        resultado = scenario_node(_state_valido())
        assert resultado["escenarios"]["base"]["dscr"] == Decimal("1.50")

    def test_escenario_optimista_dscr_correcto(self):
        """optimista DSCR = (12M - 7M) / 2M = 2.50."""
        resultado = scenario_node(_state_valido())
        assert resultado["escenarios"]["optimista"]["dscr"] == Decimal("2.50")

    def test_escenario_pesimista_dscr_correcto(self):
        """pesimista DSCR = (8M - 7M) / 2M = 0.50."""
        resultado = scenario_node(_state_valido())
        assert resultado["escenarios"]["pesimista"]["dscr"] == Decimal("0.50")

    def test_cada_escenario_tiene_clasificacion(self):
        """Cada escenario incluye clasificacion — node es autocontenido."""
        resultado = scenario_node(_state_valido())
        assert resultado["escenarios"]["base"]["clasificacion"] == "viable"
        assert resultado["escenarios"]["optimista"]["clasificacion"] == "viable"
        assert resultado["escenarios"]["pesimista"]["clasificacion"] == "critico"

    def test_todos_dscr_son_decimal(self):
        """Decisión #7: ningún dscr es float."""
        resultado = scenario_node(_state_valido())
        for nombre in ("base", "optimista", "pesimista"):
            assert isinstance(resultado["escenarios"][nombre]["dscr"], Decimal)

    def test_propaga_error_previo_sin_ejecutar(self):
        """Decisión #2: si state['error'] no es None, retorna sin calcular."""
        state = _state_valido(error="intake falló")
        resultado = scenario_node(state)
        assert resultado["error"] == "intake falló"
        assert resultado["escenarios"] is None  # no se modificó

    def test_cuota_cero_no_lanza_excepcion(self):
        """Cuota = 0 (empresa sin deuda) se maneja sin excepción."""
        state = _state_valido(cuota_mensual=Decimal("0"))
        resultado = scenario_node(state)
        assert resultado["error"] is None
        assert resultado["escenarios"] is not None
