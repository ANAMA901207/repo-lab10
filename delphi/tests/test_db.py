# delphi/tests/test_db.py

import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, call

import delphi.db as db


def _make_client(insert_data: list[dict] | None = None) -> MagicMock:
    """Devuelve un mock del supabase Client con cadena table(...).insert(...).execute()."""
    mock_client = MagicMock()
    data = insert_data if insert_data is not None else [{"id": "uuid-sesion-123"}]
    mock_client.table.return_value.insert.return_value.execute.return_value.data = data
    mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock()
    return mock_client


class TestCrearSesion:
    def test_retorna_uuid_de_respuesta(self):
        """crear_sesion devuelve el id generado por Supabase."""
        cliente = _make_client([{"id": "abc-123"}])
        resultado = db.crear_sesion(cliente, "anonimo", "comercio")

        assert resultado == "abc-123"

    def test_inserta_en_tabla_sesiones(self):
        """crear_sesion llama a table('sesiones').insert(...)."""
        cliente = _make_client()
        db.crear_sesion(cliente, "anonimo", "servicios")

        cliente.table.assert_called_with("sesiones")
        insercion = cliente.table.return_value.insert.call_args[0][0]
        assert insercion["usuario_id"] == "anonimo"
        assert insercion["sector"] == "servicios"


class TestGuardarDatosFinancieros:
    def test_inserta_en_tabla_correcta(self):
        cliente = _make_client()
        db.guardar_datos_financieros(
            cliente,
            sesion_id="sid-1",
            ingresos_mensuales=Decimal("10000000"),
            gastos_mensuales=Decimal("7000000"),
            deuda_total=Decimal("50000000"),
            cuota_mensual=Decimal("2000000"),
            fecha_corte=date(2025, 3, 31),
        )

        cliente.table.assert_called_with("datos_financieros")

    def test_campos_numericos_son_float(self):
        """Los Decimal se convierten a float antes de insertar (Supabase NUMERIC)."""
        cliente = _make_client()
        db.guardar_datos_financieros(
            cliente,
            sesion_id="sid-1",
            ingresos_mensuales=Decimal("10000000"),
            gastos_mensuales=Decimal("7000000"),
            deuda_total=Decimal("50000000"),
            cuota_mensual=Decimal("2000000"),
            fecha_corte=date(2025, 3, 31),
        )

        payload = cliente.table.return_value.insert.call_args[0][0]
        assert isinstance(payload["ingresos_mensuales"], float)
        assert isinstance(payload["gastos_mensuales"], float)
        assert isinstance(payload["deuda_total"], float)
        assert isinstance(payload["cuota_mensual"], float)

    def test_fecha_corte_como_isoformat(self):
        """fecha_corte se serializa como string ISO 8601 antes del INSERT."""
        cliente = _make_client()
        db.guardar_datos_financieros(
            cliente,
            sesion_id="sid-1",
            ingresos_mensuales=Decimal("1"),
            gastos_mensuales=Decimal("1"),
            deuda_total=Decimal("1"),
            cuota_mensual=Decimal("1"),
            fecha_corte=date(2025, 12, 15),
        )

        payload = cliente.table.return_value.insert.call_args[0][0]
        assert payload["fecha_corte"] == "2025-12-15"

    def test_fecha_corte_none_queda_none(self):
        """Si fecha_corte es None, el payload la envía como None."""
        cliente = _make_client()
        db.guardar_datos_financieros(
            cliente,
            sesion_id="sid-1",
            ingresos_mensuales=Decimal("1"),
            gastos_mensuales=Decimal("1"),
            deuda_total=Decimal("1"),
            cuota_mensual=Decimal("1"),
            fecha_corte=None,
        )

        payload = cliente.table.return_value.insert.call_args[0][0]
        assert payload["fecha_corte"] is None


class TestGuardarResultados:
    def test_inserta_en_tabla_resultados(self):
        cliente = _make_client()
        db.guardar_resultados(
            cliente,
            sesion_id="sid-1",
            dscr_base=Decimal("1.50"),
            dscr_optimista=Decimal("1.80"),
            dscr_pesimista=Decimal("1.20"),
            veredicto="saludable",
            recomendaciones=["Rec A", "Rec B", "Rec C"],
        )

        cliente.table.assert_called_with("resultados")

    def test_dscr_convertidos_a_float(self):
        """Los DSCR Decimal se convierten a float para NUMERIC en Supabase."""
        cliente = _make_client()
        db.guardar_resultados(
            cliente,
            sesion_id="sid-1",
            dscr_base=Decimal("1.50"),
            dscr_optimista=Decimal("1.80"),
            dscr_pesimista=Decimal("1.20"),
            veredicto="saludable",
            recomendaciones=["Rec A"],
        )

        payload = cliente.table.return_value.insert.call_args[0][0]
        assert isinstance(payload["dscr_base"], float)
        assert isinstance(payload["dscr_optimista"], float)
        assert isinstance(payload["dscr_pesimista"], float)

    def test_recomendaciones_como_lista(self):
        """recomendaciones se envía como lista (JSONB en Supabase)."""
        cliente = _make_client()
        recs = ["A", "B", "C"]
        db.guardar_resultados(
            cliente,
            sesion_id="sid-1",
            dscr_base=Decimal("1"),
            dscr_optimista=Decimal("1"),
            dscr_pesimista=Decimal("1"),
            veredicto="saludable",
            recomendaciones=recs,
        )

        payload = cliente.table.return_value.insert.call_args[0][0]
        assert payload["recomendaciones"] == recs


class TestGuardarMensajes:
    def test_inserta_dos_mensajes(self):
        """guardar_mensajes inserta usuario y asistente en un solo INSERT."""
        cliente = _make_client()
        db.guardar_mensajes(cliente, "sid-1", "hola", "Veredicto: SALUDABLE")

        cliente.table.assert_called_with("mensajes")
        filas = cliente.table.return_value.insert.call_args[0][0]
        assert len(filas) == 2

    def test_roles_correctos(self):
        """Los roles deben ser 'usuario' y 'asistente'."""
        cliente = _make_client()
        db.guardar_mensajes(cliente, "sid-1", "hola", "respuesta")

        filas = cliente.table.return_value.insert.call_args[0][0]
        roles = {f["rol"] for f in filas}
        assert roles == {"usuario", "asistente"}

    def test_contenidos_correctos(self):
        """Cada fila lleva su contenido correspondiente."""
        cliente = _make_client()
        db.guardar_mensajes(cliente, "sid-1", "mi mensaje", "mi respuesta")

        filas = cliente.table.return_value.insert.call_args[0][0]
        por_rol = {f["rol"]: f["contenido"] for f in filas}
        assert por_rol["usuario"] == "mi mensaje"
        assert por_rol["asistente"] == "mi respuesta"


class TestCompletarSesion:
    def test_actualiza_estado_a_completado(self):
        """completar_sesion llama UPDATE con estado='completado'."""
        cliente = _make_client()
        db.completar_sesion(cliente, "sid-1")

        cliente.table.assert_called_with("sesiones")
        payload = cliente.table.return_value.update.call_args[0][0]
        assert payload["estado"] == "completado"

    def test_filtra_por_sesion_id(self):
        """El UPDATE filtra por el id correcto."""
        cliente = _make_client()
        db.completar_sesion(cliente, "sid-xyz")

        cliente.table.return_value.update.return_value.eq.assert_called_with("id", "sid-xyz")
