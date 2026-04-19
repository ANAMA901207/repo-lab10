# delphi/tests/test_intake_agent.py

import json
import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock

from delphi.graph.delphi_graph import initial_state
from delphi.agents.intake_agent import intake_node


def _mock_response(json_dict: dict) -> MagicMock:
    """Construye un objeto de respuesta falso de Gemini."""
    mock = MagicMock()
    mock.text = json.dumps(json_dict)
    return mock


_DATOS_VALIDOS = {
    "ingresos_mensuales": 10000000,
    "gastos_mensuales": 7000000,
    "deuda_total": 50000000,
    "cuota_mensual": 2000000,
    "sector": "comercio",
}


class TestIntakeNode:
    @patch("delphi.agents.intake_agent.genai.Client")
    def test_caso_feliz_popula_state(self, mock_client_cls):
        """Gemini retorna JSON válido → State actualizado con los 5 campos."""
        mock_client_cls.return_value.models.generate_content.return_value = _mock_response(_DATOS_VALIDOS)
        state = initial_state("tengo ingresos de 10 millones, gastos de 7")

        resultado = intake_node(state)

        assert resultado["error"] is None
        assert resultado["ingresos_mensuales"] == Decimal("10000000")
        assert resultado["gastos_mensuales"] == Decimal("7000000")
        assert resultado["deuda_total"] == Decimal("50000000")
        assert resultado["cuota_mensual"] == Decimal("2000000")
        assert resultado["sector"] == "comercio"

    @patch("delphi.agents.intake_agent.genai.Client")
    def test_datos_extraidos_son_decimal(self, mock_client_cls):
        """Decisión #7: los campos financieros se almacenan como Decimal, nunca float."""
        mock_client_cls.return_value.models.generate_content.return_value = _mock_response(_DATOS_VALIDOS)
        resultado = intake_node(initial_state("test"))

        for campo in ("ingresos_mensuales", "gastos_mensuales", "deuda_total", "cuota_mensual"):
            assert isinstance(resultado[campo], Decimal), f"{campo} debe ser Decimal"

    @patch("delphi.agents.intake_agent.genai.Client")
    def test_error_api_escribe_error_en_state(self, mock_client_cls):
        """Si Gemini lanza excepción, el error se captura y no se propaga."""
        mock_client_cls.return_value.models.generate_content.side_effect = Exception("API timeout")
        resultado = intake_node(initial_state("test"))

        assert resultado["error"] is not None
        assert "intake" in resultado["error"].lower() or "timeout" in resultado["error"].lower()

    @patch("delphi.agents.intake_agent.genai.Client")
    def test_json_invalido_escribe_error_en_state(self, mock_client_cls):
        """Si Gemini retorna texto no parseable como JSON, se escribe error en State."""
        mock = MagicMock()
        mock.text = "Lo siento, no entendí la pregunta."
        mock_client_cls.return_value.models.generate_content.return_value = mock

        resultado = intake_node(initial_state("test"))

        assert resultado["error"] is not None

    @patch("delphi.agents.intake_agent.genai.Client")
    def test_json_con_campos_faltantes_escribe_error(self, mock_client_cls):
        """JSON válido pero sin campos requeridos → ValidationError de Pydantic → error en State."""
        mock_client_cls.return_value.models.generate_content.return_value = _mock_response(
            {"sector": "comercio"}  # faltan todos los campos numéricos
        )
        resultado = intake_node(initial_state("test"))

        assert resultado["error"] is not None

    def test_propaga_error_previo_sin_llamar_llm(self):
        """Decisión #2: si state['error'] no es None, retorna sin llamar a Gemini."""
        state = initial_state("test")
        state["error"] = "error anterior"

        with patch("delphi.agents.intake_agent.genai.Client") as mock_client_cls:
            resultado = intake_node(state)
            mock_client_cls.assert_not_called()

        assert resultado["error"] == "error anterior"

    @patch("delphi.agents.intake_agent.genai.Client")
    def test_mensaje_original_se_preserva(self, mock_client_cls):
        """El mensaje_usuario no se modifica después de intake."""
        mock_client_cls.return_value.models.generate_content.return_value = _mock_response(_DATOS_VALIDOS)
        msg = "mis ingresos son 10 millones"
        resultado = intake_node(initial_state(msg))

        assert resultado["mensaje_usuario"] == msg
