# Plantilla Maestra de Briefs — Delphi CFO Virtual

> Archivo reutilizable. Copiar y completar para cada tarea nueva.
> Proyecto: Delphi | Stack: Python · LangGraph · Gemini API · Streamlit · Supabase
> Repositorio: repo-lab10/delphi/

---

## 1. Título de la tarea

`[Nombre corto y descriptivo de la tarea]`

Ejemplo: `Implementar Intake Agent — captura conversacional de datos financieros`

---

## 2. Contexto

### Sistema actual
`[Describe el estado actual del proyecto en el momento de esta tarea]`

Ejemplo:
> Delphi es un CFO virtual para dueños de PyMEs colombianas. El canal de interacción es Streamlit (chat conversacional). El usuario escribe en lenguaje natural y Delphi responde con análisis financiero, escenarios y recomendaciones concretas. El grafo LangGraph orquesta los agentes. El LLM principal es gemini-2.0-flash via Google AI Studio. La base de datos es Supabase (PostgreSQL). Todo el proyecto vive dentro del repositorio repo-lab10, en la carpeta delphi/.

### Problema que se resuelve
`[¿Qué falla, falta o bloquea sin esta tarea?]`

### Objetivo concreto
`[Una sola oración: qué debe quedar funcionando al terminar]`

---

## 3. Requerimientos técnicos

| Elemento | Detalle |
|---|---|
| Lenguaje | Python 3.11+ |
| Orquestación | LangGraph (StateGraph) |
| LLM | Gemini API — modelo: gemini-2.0-flash |
| Canal UI | Streamlit (chat conversacional) |
| Base de datos | Supabase (PostgreSQL via supabase-py) |
| Patrón de agente | Nodo del grafo con State tipado |
| Input esperado | `[describir estructura del input]` |
| Output esperado | `[describir estructura del output]` |
| Integraciones | `[otras tablas de Supabase, otros agentes del grafo]` |

---

## 4. Constraints

- Usar **type hints** en todas las funciones
- Cada función nueva debe tener su **test unitario antes** de integrar al grafo (TDD)
- No usar librerías fuera de: `langgraph`, `google-generativeai`, `streamlit`, `supabase-py`, `pydantic`, `weasyprint`, `python-dotenv`
- El State del grafo debe ser un **TypedDict** con campos explícitos
- No hardcodear credenciales — usar `.env` y `python-dotenv`
- Los prompts del sistema deben vivir en archivos separados (`delphi/prompts/`)
- El código debe pasar el linter del proyecto (`ruff`)
- Ningún nodo del grafo debe tener más de 50 líneas — extraer a funciones helper si es necesario
- Todo el código vive en `repo-lab10/delphi/`

---

## 5. Definition of Done

- [ ] Tests unitarios escritos **antes** del código (TDD)
- [ ] Todos los tests pasan: `X/X PASSED`
- [ ] El nodo está integrado al grafo y el flujo end-to-end funciona en Streamlit
- [ ] Type hints completos en todas las funciones nuevas
- [ ] Sin errores de linter (`ruff check .` limpio)
- [ ] El agente QA Engineer verificó y entregó reporte
- [ ] `[Criterio funcional específico de esta tarea]`
- [ ] `[Métrica de performance si aplica]`

---

## Notas adicionales

`[Contexto extra, decisiones de diseño previas, links a documentación relevante]`