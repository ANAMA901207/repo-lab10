# delphi/tests/test_financial_calc.py

import pytest
from decimal import Decimal

from delphi.skills.financial_calc import (
    calcular_dscr,
    clasificar_dscr,
    calcular_escenarios,
    EscenarioResult,
    EscenariosResult,
)


# ---------------------------------------------------------------------------
# calcular_dscr
# ---------------------------------------------------------------------------


class TestCalcularDscr:
    def test_caso_normal(self):
        """PyME con flujo positivo y deuda manejable: DSCR = 1.50."""
        resultado = calcular_dscr(
            ingresos=Decimal("10000000"),
            gastos=Decimal("7000000"),
            cuota=Decimal("2000000"),
        )
        assert resultado == Decimal("1.50")
        assert isinstance(resultado, Decimal)

    def test_caso_critico(self):
        """PyME que apenas cubre costos operativos: DSCR = 0.50."""
        resultado = calcular_dscr(
            ingresos=Decimal("5000000"),
            gastos=Decimal("4500000"),
            cuota=Decimal("1000000"),
        )
        assert resultado == Decimal("0.50")
        assert resultado < Decimal("1.0")

    def test_sin_deuda_no_divide_entre_cero(self):
        """Cuota = 0 retorna Decimal('0'), nunca ZeroDivisionError."""
        resultado = calcular_dscr(
            ingresos=Decimal("10000000"),
            gastos=Decimal("7000000"),
            cuota=Decimal("0"),
        )
        assert resultado == Decimal("0")
        assert isinstance(resultado, Decimal)

    def test_flujo_negativo_retorna_dscr_negativo(self):
        """Gastos > ingresos produce DSCR negativo, clasificado como critico."""
        resultado = calcular_dscr(
            ingresos=Decimal("5000000"),
            gastos=Decimal("7000000"),
            cuota=Decimal("1000000"),
        )
        assert resultado == Decimal("-2.00")
        assert resultado < Decimal("0")

    def test_valores_grandes(self):
        """Empresa mediana con cifras en cientos de millones COP."""
        resultado = calcular_dscr(
            ingresos=Decimal("500000000"),
            gastos=Decimal("300000000"),
            cuota=Decimal("100000000"),
        )
        assert resultado == Decimal("2.00")

    def test_acepta_float_con_conversion_interna(self):
        """Decision #1: parámetros float se convierten a Decimal internamente."""
        resultado = calcular_dscr(10_000_000.0, 7_000_000.0, 2_000_000.0)
        assert isinstance(resultado, Decimal)
        assert resultado == Decimal("1.50")

    def test_acepta_int_con_conversion_interna(self):
        """Decision #1: parámetros int se convierten a Decimal internamente."""
        resultado = calcular_dscr(10_000_000, 7_000_000, 2_000_000)
        assert isinstance(resultado, Decimal)
        assert resultado == Decimal("1.50")

    def test_redondeo_a_dos_decimales(self):
        """Decision #6: resultado redondeado a PRECISION = Decimal('0.01')."""
        # (10M - 7M) / 3M = 1.0000... → 1.00
        resultado = calcular_dscr(
            ingresos=Decimal("10000000"),
            gastos=Decimal("7000000"),
            cuota=Decimal("3000000"),
        )
        # 3M/3M = 1.0 exacto, verifica que es Decimal con 2 decimales
        assert resultado == Decimal("1.00")
        assert isinstance(resultado, Decimal)


# ---------------------------------------------------------------------------
# clasificar_dscr
# ---------------------------------------------------------------------------


class TestClasificarDscr:
    def test_umbral_viable_exacto(self):
        """Exactamente 1.25 es el límite inferior de viable."""
        assert clasificar_dscr(Decimal("1.25")) == "viable"

    def test_viable_por_encima(self):
        assert clasificar_dscr(Decimal("1.30")) == "viable"

    def test_umbral_alerta_exacto(self):
        """Exactamente 1.00 es el límite inferior de alerta."""
        assert clasificar_dscr(Decimal("1.00")) == "alerta"

    def test_alerta_entre_umbrales(self):
        assert clasificar_dscr(Decimal("1.10")) == "alerta"

    def test_critico_bajo_uno(self):
        assert clasificar_dscr(Decimal("0.99")) == "critico"

    def test_critico_cero(self):
        assert clasificar_dscr(Decimal("0.00")) == "critico"

    def test_critico_negativo(self):
        """Decision #5: DSCR negativo (gastos > ingresos) es 'critico'."""
        assert clasificar_dscr(Decimal("-1.0")) == "critico"
        assert clasificar_dscr(Decimal("-2.00")) == "critico"

    def test_acepta_float(self):
        """Decision #1: acepta float como entrada."""
        assert clasificar_dscr(1.30) == "viable"
        assert clasificar_dscr(1.10) == "alerta"
        assert clasificar_dscr(0.80) == "critico"


# ---------------------------------------------------------------------------
# calcular_escenarios
# ---------------------------------------------------------------------------


class TestCalcularEscenarios:
    def _datos_normales(self):
        return {
            "ingresos": Decimal("10000000"),
            "gastos": Decimal("7000000"),
            "cuota": Decimal("2000000"),
        }

    def test_retorna_tres_escenarios(self):
        """Decision #2: retorna TypedDict con claves base, optimista, pesimista."""
        resultado = calcular_escenarios(**self._datos_normales())
        assert "base" in resultado
        assert "optimista" in resultado
        assert "pesimista" in resultado

    def test_cada_escenario_tiene_estructura_completa(self):
        """Decision #2: cada escenario incluye ingresos, gastos, cuota, dscr, clasificacion."""
        resultado = calcular_escenarios(**self._datos_normales())
        for nombre in ("base", "optimista", "pesimista"):
            escenario = resultado[nombre]
            assert "ingresos" in escenario
            assert "gastos" in escenario
            assert "cuota" in escenario
            assert "dscr" in escenario
            assert "clasificacion" in escenario

    def test_escenario_base_usa_ingresos_originales(self):
        resultado = calcular_escenarios(**self._datos_normales())
        assert resultado["base"]["ingresos"] == Decimal("10000000")
        assert resultado["base"]["dscr"] == Decimal("1.50")

    def test_escenario_optimista_ingresos_mas_20_porciento(self):
        """Decision #4: solo los ingresos varían (+20%), gastos y cuota son fijos."""
        resultado = calcular_escenarios(**self._datos_normales())
        assert resultado["optimista"]["ingresos"] == Decimal("12000000")
        # DSCR optimista = (12M - 7M) / 2M = 2.50
        assert resultado["optimista"]["dscr"] == Decimal("2.50")

    def test_escenario_pesimista_ingresos_menos_20_porciento(self):
        """Decision #4: solo los ingresos varían (-20%), gastos y cuota son fijos."""
        resultado = calcular_escenarios(**self._datos_normales())
        assert resultado["pesimista"]["ingresos"] == Decimal("8000000")
        # DSCR pesimista = (8M - 7M) / 2M = 0.50
        assert resultado["pesimista"]["dscr"] == Decimal("0.50")

    def test_gastos_y_cuota_son_fijos_en_todos_los_escenarios(self):
        """Decision #4: simplificación v1 — gastos y cuota no cambian entre escenarios."""
        resultado = calcular_escenarios(**self._datos_normales())
        for nombre in ("base", "optimista", "pesimista"):
            assert resultado[nombre]["gastos"] == Decimal("7000000")
            assert resultado[nombre]["cuota"] == Decimal("2000000")

    def test_cada_escenario_incluye_clasificacion(self):
        """Decision #3: calcular_escenarios es autocontenida — llama clasificar_dscr internamente."""
        resultado = calcular_escenarios(**self._datos_normales())
        assert resultado["base"]["clasificacion"] == "viable"       # 1.50
        assert resultado["optimista"]["clasificacion"] == "viable"  # 2.50
        assert resultado["pesimista"]["clasificacion"] == "critico"  # 0.50

    def test_cuota_cero_propagada_sin_error(self):
        """Cuota = 0 en escenarios no lanza excepciones."""
        resultado = calcular_escenarios(
            ingresos=Decimal("10000000"),
            gastos=Decimal("7000000"),
            cuota=Decimal("0"),
        )
        for nombre in ("base", "optimista", "pesimista"):
            assert resultado[nombre]["dscr"] == Decimal("0")

    def test_acepta_float_e_int(self):
        """Decision #1: acepta float e int como entrada."""
        resultado = calcular_escenarios(10_000_000, 7_000_000, 2_000_000)
        assert isinstance(resultado["base"]["dscr"], Decimal)
        assert resultado["base"]["dscr"] == Decimal("1.50")

    def test_todos_dscr_son_decimal(self):
        """Decision #7: los valores dscr son siempre Decimal, nunca float."""
        resultado = calcular_escenarios(**self._datos_normales())
        for nombre in ("base", "optimista", "pesimista"):
            assert isinstance(resultado[nombre]["dscr"], Decimal)
