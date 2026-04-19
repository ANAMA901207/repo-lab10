# delphi/tests/test_advisor_agent.py

import json
import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock

from delphi.graph.delphi_graph import initial_state
from delphi.agents.advisor_agent import advisor_node
from delphi.skills.financial_calc import calcular_escenarios


def _mock_response(json_dict: dict) -> MagicMock:
    mock = MagicMock()
    mock.text = json.dumps(json_dict)
    return mock


def _state_con_escenarios(**kwargs):
    """Estado con escenarios ya calculados — tal como lo entrega scenario_node."""
    state = initial_state("quiero un crédito")
    state.update({
        "ingresos_mensuales": Decimal("10000000"),
        "gastos_mensuales": Decimal("7000000"),
        "cuota_mensual": Decimal("2000000"),
        "sector": "comercio",
        "escenarios": calcular_escenarios(
            ingresos=Decimal("10000000"),
            gastos=Decimal("7000000"),
            cuota=Decimal("2000000"),
        ),
    })
    state.update(kwargs)
    return state


_RESPUESTA_LLM_VALIDA = {
    "veredicto": "viable",
    "recomendaciones": [
        "Mantén un fondo de emergencia de 3 meses de gastos operativos.",
        "Negocia con el banco un período de gracia de 6 meses.",
        "Diversifica tus fuentes de ingreso antes de asumir nueva deuda.",
    ],
}


class TestAdvisorNode:
    @patch("delphi.agents.advisor_agent.genai.Client")
    def test_caso_feliz_popula_veredicto_y_recomendaciones(self, mock_client_cls):
        """Gemini retorna veredicto válido + 3 recomendaciones → State actualizado."""
        mock_client_cls.return_value.models.generate_content.return_value = _mock_response(
            _RESPUESTA_LLM_VALIDA
        )
        resultado = advisor_node(_state_con_escenarios())

        assert resultado["error"] is None
        assert resultado["veredicto"] == "viable"
        assert len(resultado["recomendaciones"]) == 3

    @patch("delphi.agents.advisor_agent.genai.Client")
    def test_recomendaciones_son_lista_de_strings(self, mock_client_cls):
        mock_client_cls.return_value.models.generate_content.return_value = _mock_response(
            _RESPUESTA_LLM_VALIDA
        )
        resultado = advisor_node(_state_con_escenarios())

        assert isinstance(resultado["recomendaciones"], list)
        for item in resultado["recomendaciones"]:
            assert isinstance(item, str)

    @patch("delphi.agents.advisor_agent.genai.Client")
    def test_guardrail_veredicto_invalido_usa_fallback_deterministico(self, mock_client_cls):
        """Decisión #4: veredicto inválido → clasificar_dscr(escenarios.base.dscr)."""
        mock_client_cls.return_value.models.generate_content.return_value = _mock_response(
            {
                "veredicto": "riesgo alto",  # inválido — no es "viable"/"alerta"/"critico"
                "recomendaciones": ["r1", "r2", "r3"],
            }
        )
        resultado = advisor_node(_state_con_escenarios())

        # base DSCR = 1.50 → clasificar_dscr → "viable"
        assert resultado["veredicto"] == "viable"
        assert resultado["error"] is None

    @patch("delphi.agents.advisor_agent.genai.Client")
    def test_guardrail_preserva_recomendaciones_del_llm(self, mock_client_cls):
        """El guardrail solo corrige el veredicto — las recomendaciones del LLM se preservan."""
        mock_client_cls.return_value.models.generate_content.return_value = _mock_response(
            {
                "veredicto": "CRITICO",  # inválido por mayúsculas
                "recomendaciones": ["r1", "r2", "r3"],
            }
        )
        resultado = advisor_node(_state_con_escenarios())

        assert resultado["recomendaciones"] == ["r1", "r2", "r3"]

    @patch("delphi.agents.advisor_agent.genai.Client")
    def test_error_api_escribe_error_en_state(self, mock_client_cls):
        """Si Gemini lanza excepción, el error se captura sin propagarse."""
        mock_client_cls.return_value.models.generate_content.side_effect = Exception("rate limit")
        resultado = advisor_node(_state_con_escenarios())

        assert resultado["error"] is not None

    @patch("delphi.agents.advisor_agent.genai.Client")
    def test_json_invalido_escribe_error_en_state(self, mock_client_cls):
        """Respuesta del LLM no parseable → error en State."""
        mock = MagicMock()
        mock.text = "No puedo analizar esto."
        mock_client_cls.return_value.models.generate_content.return_value = mock

        resultado = advisor_node(_state_con_escenarios())

        assert resultado["error"] is not None

    def test_propaga_error_previo_sin_llamar_llm(self):
        """Decisión #2: si state['error'] no es None, retorna sin llamar a Gemini."""
        state = _state_con_escenarios(error="scenario falló")

        with patch("delphi.agents.advisor_agent.genai.Client") as mock_client_cls:
            resultado = advisor_node(state)
            mock_client_cls.assert_not_called()

        assert resultado["error"] == "scenario falló"

    @patch("delphi.agents.advisor_agent.genai.Client")
    def test_veredictos_validos_se_aceptan_todos(self, mock_client_cls):
        """Los tres veredictos válidos pasan el guardrail sin fallback."""
        for veredicto in ("viable", "alerta", "critico"):
            mock_client_cls.return_value.models.generate_content.return_value = _mock_response(
                {"veredicto": veredicto, "recomendaciones": ["r1", "r2", "r3"]}
            )
            resultado = advisor_node(_state_con_escenarios())
            assert resultado["veredicto"] == veredicto
            assert resultado["error"] is None
