# delphi/tests/test_persistence_agent.py

import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import patch, MagicMock, call

from delphi.graph.delphi_graph import initial_state
from delphi.agents.persistence_agent import persistence_node


def _state_listo() -> dict:
    """State con todos los campos necesarios para persistir."""
    state = initial_state("tengo ingresos de 10 millones")
    return {
        **state,
        "ingresos_mensuales": Decimal("10000000"),
        "gastos_mensuales": Decimal("7000000"),
        "deuda_total": Decimal("50000000"),
        "cuota_mensual": Decimal("2000000"),
        "sector": "comercio",
        "fecha_corte": date(2025, 3, 31),
        "escenarios": {
            "base": {"dscr": Decimal("1.50"), "ingresos": Decimal("10000000"),
                     "gastos": Decimal("7000000"), "cuota": Decimal("2000000"),
                     "clasificacion": "saludable"},
            "optimista": {"dscr": Decimal("1.80"), "ingresos": Decimal("11000000"),
                          "gastos": Decimal("7000000"), "cuota": Decimal("2000000"),
                          "clasificacion": "saludable"},
            "pesimista": {"dscr": Decimal("1.20"), "ingresos": Decimal("9000000"),
                          "gastos": Decimal("7000000"), "cuota": Decimal("2000000"),
                          "clasificacion": "saludable"},
        },
        "veredicto": "saludable",
        "recomendaciones": ["Rec A", "Rec B", "Rec C"],
    }


class TestPersistenceNode:
    @patch("delphi.agents.persistence_agent.db")
    @patch("delphi.agents.persistence_agent._get_supabase_client")
    def test_caso_feliz_retorna_sesion_id(self, mock_get_client, mock_db):
        """El nodo guarda todo y retorna sesion_id en el state."""
        mock_db.crear_sesion.return_value = "uuid-sesion-abc"

        resultado = persistence_node(_state_listo())

        assert resultado["sesion_id"] == "uuid-sesion-abc"
        assert resultado["error_persistencia"] is None

    @patch("delphi.agents.persistence_agent.db")
    @patch("delphi.agents.persistence_agent._get_supabase_client")
    def test_llama_todas_las_funciones_de_db(self, mock_get_client, mock_db):
        """El nodo invoca las 5 funciones de db en el orden correcto."""
        mock_db.crear_sesion.return_value = "sid-1"

        persistence_node(_state_listo())

        mock_db.crear_sesion.assert_called_once()
        mock_db.guardar_datos_financieros.assert_called_once()
        mock_db.guardar_resultados.assert_called_once()
        mock_db.guardar_mensajes.assert_called_once()
        mock_db.completar_sesion.assert_called_once()

    @patch("delphi.agents.persistence_agent.db")
    @patch("delphi.agents.persistence_agent._get_supabase_client")
    def test_error_previo_no_ejecuta_nada(self, mock_get_client, mock_db):
        """Si state['error'] no es None, el nodo retorna sin tocar la BD."""
        state = _state_listo()
        state["error"] = "fallo anterior"

        resultado = persistence_node(state)

        mock_db.crear_sesion.assert_not_called()
        assert resultado["error"] == "fallo anterior"

    @patch("delphi.agents.persistence_agent.db")
    @patch("delphi.agents.persistence_agent._get_supabase_client")
    def test_fallo_crear_sesion_aborta_resto(self, mock_get_client, mock_db):
        """Si crear_sesion falla, los otros INSERTs no se ejecutan."""
        mock_db.crear_sesion.side_effect = Exception("conexión rechazada")

        resultado = persistence_node(_state_listo())

        mock_db.guardar_datos_financieros.assert_not_called()
        mock_db.guardar_resultados.assert_not_called()
        mock_db.guardar_mensajes.assert_not_called()
        mock_db.completar_sesion.assert_not_called()

    @patch("delphi.agents.persistence_agent.db")
    @patch("delphi.agents.persistence_agent._get_supabase_client")
    def test_fallo_escribe_en_error_persistencia(self, mock_get_client, mock_db):
        """Cualquier excepción en BD se registra en error_persistencia, no en error."""
        mock_db.crear_sesion.side_effect = Exception("timeout")

        resultado = persistence_node(_state_listo())

        assert resultado["error_persistencia"] is not None
        assert "timeout" in resultado["error_persistencia"]
        assert resultado["error"] is None  # state['error'] no se toca

    @patch("delphi.agents.persistence_agent.db")
    @patch("delphi.agents.persistence_agent._get_supabase_client")
    def test_sesion_id_none_si_falla(self, mock_get_client, mock_db):
        """Si la persistencia falla, sesion_id permanece None."""
        mock_db.crear_sesion.side_effect = Exception("error")
        state = _state_listo()
        state["sesion_id"] = None

        resultado = persistence_node(state)

        assert resultado["sesion_id"] is None

    @patch("delphi.agents.persistence_agent.db")
    @patch("delphi.agents.persistence_agent._get_supabase_client")
    def test_respuesta_delphi_incluye_veredicto_y_recomendaciones(self, mock_get_client, mock_db):
        """La respuesta formateada que se guarda contiene veredicto y recs."""
        mock_db.crear_sesion.return_value = "sid-1"

        persistence_node(_state_listo())

        respuesta = mock_db.guardar_mensajes.call_args.kwargs["respuesta_delphi"]
        assert "saludable" in respuesta.lower()
        assert "Rec A" in respuesta

    @patch("delphi.agents.persistence_agent.db")
    @patch("delphi.agents.persistence_agent._get_supabase_client")
    def test_completar_sesion_recibe_sesion_id_correcto(self, mock_get_client, mock_db):
        """completar_sesion se llama con el mismo UUID que retornó crear_sesion."""
        mock_db.crear_sesion.return_value = "uuid-final-xyz"

        persistence_node(_state_listo())

        mock_db.completar_sesion.assert_called_once_with(mock_get_client.return_value, "uuid-final-xyz")
