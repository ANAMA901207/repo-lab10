# Protocolo de Review — Código Generado por IA
## Proyecto: Delphi CFO Virtual
## Repositorio: repo-lab10/delphi/

> Checklist fija. Revisar punto a punto antes de hacer commit.
> Si algún punto falla — corregir antes de continuar.

---

## Punto 1 — Alucinaciones de librerías

**Pregunta:** ¿Todos los imports existen y están en el stack autorizado?

**Qué revisar:**
- Buscar cada `import` en la documentación oficial
- Confirmar que la librería está en `requirements.txt` del proyecto
- Stack autorizado: `langgraph`, `google-generativeai`, `streamlit`, `supabase-py`, `pydantic`, `weasyprint`, `python-dotenv`, `ruff`
- Si aparece algo fuera de la lista — rechazar y pedir alternativa dentro del stack

**Señal de alerta:** La IA importa `anthropic` o `openai` cuando el proyecto usa Gemini, o usa una función de `google-generativeai` que no existe en la versión instalada.

---

## Punto 2 — Lógica de negocio financiera

**Pregunta:** ¿Los cálculos financieros son correctos y manejan casos extremos?

**Qué revisar:**
- Fórmula del DSCR: `DSCR = Flujo de caja libre / Servicio de deuda mensual`
- Todos los valores monetarios usan `Decimal`, no `float`
- Condiciones límite: DSCR < 1.0 genera alerta, DSCR < 0.8 genera alerta crítica
- El health score está en rango [0, 100] siempre

**Prueba de estrés obligatoria:**
Ingresar manualmente un flujo de caja de cero o negativo y verificar que el agente:
- No divide entre cero
- No alucina un veredicto positivo
- Retorna un mensaje de error estructurado al State con el campo `error` poblado

**Señal de alerta:** La IA calcula `utilidad_neta / deuda_total` como DSCR, o usa `float` para valores en COP.

---

## Punto 3 — Seguridad

**Pregunta:** ¿El código es seguro para manejar datos financieros de usuarios reales?

**Qué revisar:**
- No hay credenciales hardcodeadas (API keys, URLs de Supabase)
- Los inputs del usuario desde Streamlit se validan con Pydantic antes de procesar
- No hay queries SQL con concatenación de strings — usar parámetros de supabase-py
- Las respuestas del LLM no se ejecutan como código (`eval`, `exec` prohibidos)
- Los datos financieros del usuario no se loggean en texto plano

**Señal de alerta:** Aparece `GEMINI_API_KEY = "AIza..."` directo en el código.

---

## Punto 4 — Pérdida de contexto del brief

**Pregunta:** ¿La IA respetó todos los constraints y requerimientos del brief?

**Qué revisar:**
- ¿El nodo usa `TypedDict` para el State con el campo `error: Optional[str]`?
- ¿Los prompts están en `delphi/prompts/` y no hardcodeados en el nodo?
- ¿La función tiene type hints completos?
- ¿El output tiene la estructura exacta que especificó el brief?
- ¿El código está dentro de `repo-lab10/delphi/`?
- ¿Se integró al grafo en el lugar correcto?
- ¿La respuesta del LLM pasa por una validación de esquema Pydantic antes de ser usada o mostrada al usuario?

**Señal de alerta:** La IA genera un script standalone que no está diseñado como nodo del grafo LangGraph, o usa la respuesta del LLM directamente sin validar su estructura.

---

## Punto 5 — Tests, calidad y automatización

**Pregunta:** ¿El código tiene tests, pasa el linter y es compatible con procesos automáticos?

**Qué revisar:**
- Ejecutar: `pytest tests/ -v` — todos deben pasar
- Ejecutar: `ruff check .` — sin errores
- Los tests cubren: caso feliz, caso edge (valores extremos), caso de error (input inválido), flujo de caja cero o negativo
- Los mocks de Gemini API usan `unittest.mock` — no llamadas reales en tests
- El nodo nuevo tiene al menos 3 tests unitarios antes de integrarse al grafo
- La UI de Streamlit renderiza correctamente la respuesta del agente
- Si el nodo será invocado por un cron job (tarea programada): verificar que no contiene lógica de aprobación humana (HITL) que bloquee el proceso automático. Los flujos automáticos deben tener un bypass explícito del HITL

**Señal de alerta:** La IA entrega código sin tests, o un nodo automatizado queda esperando aprobación humana indefinidamente bloqueando el cron job.

---

## Resultado del review

| Punto | Estado | Observación |
|---|---|---|
| 1. Alucinaciones | OK / FALLA | |
| 2. Lógica financiera | OK / FALLA | |
| 3. Seguridad | OK / FALLA | |
| 4. Pérdida de contexto | OK / FALLA | |
| 5. Tests y calidad | OK / FALLA | |

**Decisión:** `APROBADO PARA COMMIT` / `REQUIERE CORRECCIONES`

---

