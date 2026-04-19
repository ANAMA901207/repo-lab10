# Skill: financial-testing

## Descripcion
Escribe tests para funciones de logica financiera en `delphi/skills/financial_calc.py`.
Las funciones financieras tienen casos edge criticos que un test generico no cubre.
Este skill garantiza que se prueben los casos que importan en credito.

---

## Antes de empezar

Confirma con el usuario:
- Que funcion se va a testear
- Que calcula esa funcion
- Cuales son los valores de entrada esperados

---

## Casos que SIEMPRE se deben testear

### 1. Caso feliz — valores normales de una PyME colombiana

```python
def test_dscr_caso_normal():
    """PyME con flujo positivo y deuda manejable."""
    ingresos = Decimal("10000000")   # 10 millones COP
    gastos = Decimal("7000000")      # 7 millones COP
    cuota = Decimal("2000000")       # 2 millones COP
    
    resultado = calcular_dscr(ingresos, gastos, cuota)
    
    assert resultado == Decimal("1.5")
    assert isinstance(resultado, Decimal)  # nunca float
```

### 2. Caso critico — DSCR menor a 1.0

```python
def test_dscr_caso_critico():
    """PyME que no puede cubrir su deuda."""
    ingresos = Decimal("5000000")
    gastos = Decimal("4500000")
    cuota = Decimal("1000000")
    
    resultado = calcular_dscr(ingresos, gastos, cuota)
    
    assert resultado < Decimal("1.0")
    assert clasificar_dscr(resultado) == "critico"
```

### 3. Caso edge — sin deuda (cuota cero)

```python
def test_dscr_sin_deuda():
    """PyME sin obligaciones financieras — no debe dividir entre cero."""
    ingresos = Decimal("10000000")
    gastos = Decimal("7000000")
    cuota = Decimal("0")
    
    resultado = calcular_dscr(ingresos, gastos, cuota)
    
    assert resultado == Decimal("0")  # o el valor que se defina para este caso
    # Lo importante: no lanza ZeroDivisionError
```

### 4. Caso edge — flujo de caja negativo

```python
def test_dscr_flujo_negativo():
    """PyME con gastos mayores a ingresos."""
    ingresos = Decimal("5000000")
    gastos = Decimal("7000000")    # gastos mayores que ingresos
    cuota = Decimal("1000000")
    
    resultado = calcular_dscr(ingresos, gastos, cuota)
    
    assert resultado < Decimal("0")
    assert clasificar_dscr(resultado) == "critico"
```

### 5. Caso edge — valores muy grandes

```python
def test_dscr_valores_grandes():
    """Empresa mediana con cifras en miles de millones."""
    ingresos = Decimal("500000000")   # 500 millones COP
    gastos = Decimal("300000000")
    cuota = Decimal("100000000")
    
    resultado = calcular_dscr(ingresos, gastos, cuota)
    
    assert resultado == Decimal("2.0")
    assert isinstance(resultado, Decimal)
```

### 6. Verificacion de umbrales

```python
def test_clasificacion_umbrales():
    """Los tres umbrales del DSCR son exactamente los definidos."""
    assert clasificar_dscr(Decimal("1.25")) == "viable"
    assert clasificar_dscr(Decimal("1.30")) == "viable"
    assert clasificar_dscr(Decimal("1.00")) == "alerta"
    assert clasificar_dscr(Decimal("1.10")) == "alerta"
    assert clasificar_dscr(Decimal("0.99")) == "critico"
    assert clasificar_dscr(Decimal("0.00")) == "critico"
    assert clasificar_dscr(Decimal("-1.0")) == "critico"
```

---

## Estructura del archivo de tests

```python
# delphi/tests/test_financial_calc.py

import pytest
from decimal import Decimal
from delphi.skills.financial_calc import calcular_dscr, clasificar_dscr


# --- Tests de calcular_dscr ---

def test_dscr_caso_normal():
    ...

def test_dscr_caso_critico():
    ...

def test_dscr_sin_deuda():
    ...

def test_dscr_flujo_negativo():
    ...

def test_dscr_valores_grandes():
    ...


# --- Tests de clasificar_dscr ---

def test_clasificacion_umbrales():
    ...
```

---

## Verificacion

```bash
pytest delphi/tests/test_financial_calc.py -v
```

Todos los tests deben pasar antes de integrar la funcion al grafo.