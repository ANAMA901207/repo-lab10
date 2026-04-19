# Protocolo de Review — Código Generado por IA
## Proyecto: Delphi CFO Virtual
## Repositorio: repo-lab10/delphi/

> Checklist fija. Revisar punto a punto antes de hacer commit.
> Si algún punto falla → corregir antes de continuar.

---

## Punto 1 — Alucinaciones de librerías

**Pregunta:** ¿Todos los imports existen y están en el stack autorizado?

**Qué revisar:**
- Buscar cada `import` en la documentación oficial
- Confirmar que la librería está en `requirements.txt` del proyecto
- Stack autorizado: `langgraph`, `google-generativeai`, `streamlit`, `supabase-py`, `pydantic`, `weasyprint`, `python-dotenv`, `ruff`
- Si aparece algo fuera de la lista → rechazar y pedir alternativa dentro del stack

**Señal de alerta:** La IA importa `anthropic` o `openai` cuando el proyecto usa Gemini, o usa una función de `google-generativeai` que no existe en la versión instalada.

---

## Punto 2 — Lógica de negocio financiera

**Pregunta:** ¿Los cálculos financieros son correctos para el contexto colombiano?

**Qué revisar:**
- Fórmula del DSCR: `DSCR = Flujo de caja libre / Servicio de deuda anual`
- Redondeos monetarios: usar `round(x, 2)` o `Decimal` — nunca `float` directo para COP
- Condiciones límite: DSCR < 1.0 → alerta, DSCR < 0.8 → riesgo crítico
- El health score debe estar en rango [0, 100] siempre

**Señal de alerta:** La IA calcula `utilidad_neta / deuda_total` como DSCR — eso es incorrecto.

---

## Punto 3 — Seguridad

**Pregunta:** ¿El código es seguro para manejar datos financieros de usuarios reales?

**Qué revisar:**
- No hay credenciales hardcodeadas (API keys, URLs de Supabase)
- Los inputs del usuario desde Streamlit se validan con Pydantic antes de procesar
- No hay queries SQL con concatenación de strings → usar parámetros de supabase-py
- Las respuestas del LLM no se ejecutan como código (`eval`, `exec` prohibidos)
- Los datos financieros del usuario no se loggean en texto plano

**Señal de alerta:** Aparece `GEMINI_API_KEY = "AIza..."` directo en el código.

---

## Punto 4 — Pérdida de contexto del brief

**Pregunta:** ¿La IA respetó todos los constraints y requerimientos del brief?

**Qué revisar:**
- ¿El nodo usa `TypedDict` para el State? (constraint del proyecto)
- ¿Los prompts están en `delphi/prompts/` y no hardcodeados en el nodo?
- ¿La función tiene type hints completos?
- ¿El output tiene la estructura exacta que especificó el brief?
- ¿El código está dentro de `repo-lab10/delphi/` y no en otra carpeta?
- ¿Se integró al grafo en el lugar correcto (antes/después del nodo que corresponde)?

**Señal de alerta:** La IA genera un script standalone que funciona solo pero no está diseñado como nodo del grafo LangGraph.

---

## Punto 5 — Tests y calidad (stack específico Delphi)

**Pregunta:** ¿El código tiene tests y pasa el linter del proyecto?

**Qué revisar:**
- Ejecutar: `pytest tests/ -v` → todos deben pasar
- Ejecutar: `ruff check .` → sin errores
- Los tests cubren: caso feliz, caso edge (valores extremos), caso de error (input inválido)
- Los mocks de Gemini API usan `unittest.mock` — no llamadas reales en tests
- El nodo nuevo tiene al menos 3 tests unitarios antes de integrarse al grafo
- La UI de Streamlit renderiza correctamente la respuesta del agente

**Señal de alerta:** La IA entrega código sin tests, o los tests llaman a la API real de Gemini (costo innecesario y tests no determinísticos).

---

## Resultado del review

| Punto | Estado | Observación |
|---|---|---|
| 1. Alucinaciones | ✅ / ❌ | |
| 2. Lógica financiera | ✅ / ❌ | |
| 3. Seguridad | ✅ / ❌ | |
| 4. Pérdida de contexto | ✅ / ❌ | |
| 5. Tests y calidad | ✅ / ❌ | |

**Decisión:** `APROBADO para commit` / `REQUIERE CORRECCIONES`

---

*Protocolo versión 1.2 — Proyecto Delphi — repo-lab10*