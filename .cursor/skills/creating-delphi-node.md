# Skill: creating-delphi-node

## Descripcion
Crea un nuevo nodo del grafo LangGraph en Delphi siguiendo TDD estricto.
Primero los tests, luego la implementacion. Nunca al reves.

---

## Antes de empezar

Confirma estos datos con el usuario:
- Nombre del nodo
- Que datos recibe del State
- Que datos escribe en el State
- Si incluye llamada al LLM o es logica pura

---

## Paso 1 — Escribir los tests primero (RED)

Crear el archivo `delphi/tests/test_[nombre_nodo].py` con tres tests:

```python
import pytest
from unittest.mock import patch
from delphi.graph.delphi_graph import DelphiState

def test_caso_feliz():
    """El nodo procesa correctamente un input valido."""
    state: DelphiState = {
        # datos validos completos
    }
    resultado = [nombre_funcion](state)
    assert resultado["error"] is None
    assert # criterio esperado

def test_caso_edge():
    """El nodo maneja valores extremos — cero, negativos, muy grandes."""
    state: DelphiState = {
        # valores limite
    }
    resultado = [nombre_funcion](state)
    assert # comportamiento esperado

def test_error_api():
    """El nodo maneja errores del LLM sin lanzar excepciones."""
    with patch("delphi.agents.[nombre_nodo].genai") as mock:
        mock.side_effect = Exception("API error")
        state: DelphiState = { # datos validos }
        resultado = [nombre_funcion](state)
        assert resultado["error"] is not None
```

Verificar que los tests FALLAN antes de continuar:
```bash
pytest delphi/tests/test_[nombre_nodo].py -v
# Esperado: FAILED
```

Si los tests no fallan, el test esta mal escrito. Corregir antes de continuar.

---

## Paso 2 — Implementar el nodo (GREEN)

Crear `delphi/agents/[nombre_nodo].py`:

```python
from decimal import Decimal
from typing import Optional
import google.generativeai as genai
from delphi.graph.delphi_graph import DelphiState


def [nombre_funcion](state: DelphiState) -> DelphiState:
    """
    [Descripcion del nodo]

    Args:
        state: Estado actual del grafo Delphi.

    Returns:
        Estado actualizado.
    """
    try:
        # logica del nodo
        # calculos financieros → llamar funciones de financial_calc.py
        # el LLM solo genera texto, nunca numeros criticos

        return {**state, "error": None}

    except Exception as e:
        return {**state, "error": str(e)}
```

Reglas obligatorias:
- Valores monetarios usan `Decimal`, nunca `float`
- Llamadas al LLM dentro de `try/except`
- Prompts se leen desde `delphi/prompts/[nombre].txt`
- Maximo 50 lineas de logica por nodo

Verificar que los tests PASAN:
```bash
pytest delphi/tests/test_[nombre_nodo].py -v
# Esperado: PASSED
```

---

## Paso 3 — Limpiar el codigo (REFACTOR)

Con los tests en verde:
- Extraer logica repetida a funciones helper
- Verificar que el nodo tiene menos de 50 lineas
- Correr linter:
```bash
ruff check delphi/
```

---

## Paso 4 — Integrar al grafo

Agregar en `delphi/graph/delphi_graph.py`:

```python
from delphi.agents.[nombre_nodo] import [nombre_funcion]

graph.add_node("[nombre_nodo]", [nombre_funcion])
graph.add_edge("[nodo_anterior]", "[nombre_nodo]")
```

---

## Paso 5 — Delegar al SubAgent QA

No correr los tests finales manualmente.
Invocar al SubAgent QA Engineer y esperar su reporte.
Solo hacer commit si el reporte dice APROBADO.