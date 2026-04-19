# delphi/skills/financial_calc.py

from decimal import Decimal, ROUND_HALF_UP
from typing import TypedDict, Union

# Decisión #6: precisión fija para todos los valores DSCR.
PRECISION = Decimal("0.01")

# Decisión #1: los tres tipos numéricos aceptados como entrada.
NumericInput = Union[Decimal, int, float]


class EscenarioResult(TypedDict):
    ingresos: Decimal
    gastos: Decimal
    cuota: Decimal
    dscr: Decimal
    clasificacion: str


class EscenariosResult(TypedDict):
    base: EscenarioResult
    optimista: EscenarioResult
    pesimista: EscenarioResult


def _to_decimal(value: NumericInput) -> Decimal:
    """Convierte int, float o Decimal a Decimal usando str() para evitar errores de representación binaria."""
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def calcular_dscr(
    ingresos: NumericInput,
    gastos: NumericInput,
    cuota: NumericInput,
) -> Decimal:
    """Calcula el DSCR (Debt Service Coverage Ratio).

    DSCR = (ingresos - gastos) / cuota

    Un DSCR negativo indica que los gastos superan a los ingresos; sigue siendo
    clasificado como 'critico'. Si cuota es cero retorna Decimal('0') para evitar
    ZeroDivisionError (empresa sin obligaciones de deuda).

    Args:
        ingresos: Ingresos mensuales. Acepta Decimal, int o float.
        gastos:   Gastos mensuales. Acepta Decimal, int o float.
        cuota:    Cuota mensual de deuda. Acepta Decimal, int o float.

    Returns:
        DSCR redondeado a dos decimales (PRECISION = 0.01), siempre Decimal.
    """
    ingresos_d = _to_decimal(ingresos)
    gastos_d = _to_decimal(gastos)
    cuota_d = _to_decimal(cuota)

    if cuota_d == Decimal("0"):
        return Decimal("0")

    dscr = (ingresos_d - gastos_d) / cuota_d
    return dscr.quantize(PRECISION, rounding=ROUND_HALF_UP)


def clasificar_dscr(dscr: NumericInput) -> str:
    """Clasifica un valor DSCR en tres categorías de riesgo crediticio.

    >= 1.25  →  "viable"   — empresa puede asumir la deuda con margen de seguridad
    >= 1.00  →  "alerta"   — empresa cubre la deuda pero sin colchón
    <  1.00  →  "critico"  — incluye valores negativos (gastos > ingresos)

    Args:
        dscr: Valor DSCR. Acepta Decimal, int o float.

    Returns:
        "viable", "alerta" o "critico".
    """
    dscr_d = _to_decimal(dscr)

    if dscr_d >= Decimal("1.25"):
        return "viable"
    if dscr_d >= Decimal("1.00"):
        return "alerta"
    return "critico"


def _construir_escenario(
    ingresos: Decimal,
    gastos: Decimal,
    cuota: Decimal,
) -> EscenarioResult:
    dscr = calcular_dscr(ingresos, gastos, cuota)
    return EscenarioResult(
        ingresos=ingresos,
        gastos=gastos,
        cuota=cuota,
        dscr=dscr,
        clasificacion=clasificar_dscr(dscr),
    )


def calcular_escenarios(
    ingresos: NumericInput,
    gastos: NumericInput,
    cuota: NumericInput,
) -> EscenariosResult:
    """Calcula el DSCR en tres escenarios financieros.

    Simplificación v1: gastos y cuota son fijos en todos los escenarios.
    Solo varía el nivel de ingresos:
      - base:      ingresos actuales
      - optimista: ingresos × 1.20  (+20 %)
      - pesimista: ingresos × 0.80  (−20 %)

    Cada escenario es autocontenido: incluye ingresos, gastos, cuota, DSCR y
    clasificación, sin necesidad de llamar a funciones adicionales.

    Args:
        ingresos: Ingresos mensuales base. Acepta Decimal, int o float.
        gastos:   Gastos mensuales (fijos en todos los escenarios).
        cuota:    Cuota mensual de deuda (fija en todos los escenarios).

    Returns:
        EscenariosResult con estructura completa para base, optimista y pesimista.
    """
    ingresos_d = _to_decimal(ingresos)
    gastos_d = _to_decimal(gastos)
    cuota_d = _to_decimal(cuota)

    return EscenariosResult(
        base=_construir_escenario(ingresos_d, gastos_d, cuota_d),
        optimista=_construir_escenario(
            ingresos_d * Decimal("1.20"), gastos_d, cuota_d
        ),
        pesimista=_construir_escenario(
            ingresos_d * Decimal("0.80"), gastos_d, cuota_d
        ),
    )
