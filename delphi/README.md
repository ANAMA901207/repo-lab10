# Delphi — CFO Virtual para PyMEs Colombianas

> Agente de inteligencia artificial conversacional que analiza la situación financiera de dueños de pequeñas y medianas empresas colombianas, calcula indicadores clave de riesgo y entrega recomendaciones concretas en lenguaje natural.

---

## 1. Brief del Proyecto

### Problema que resuelve
El dueño de una PyME colombiana toma decisiones financieras críticas —endeudarse, expandirse, contratar— sin acceso a acompañamiento financiero calificado. No puede pagar un CFO. No entiende los estados financieros. Toma decisiones por intuición y termina en problemas de flujo de caja o en default.

### Solución
Delphi es un CFO virtual conversacional. El usuario escribe en lenguaje natural —como si le explicara su situación a un contador de confianza— y Delphi responde con un análisis financiero estructurado, escenarios de riesgo y recomendaciones accionables.

### Usuario objetivo
Dueño de PyME colombiana con ingresos entre $50M y $2.000M COP anuales, sin equipo financiero interno, que toma decisiones de endeudamiento o inversión sin asesoría profesional.

### Caso de uso principal
Un dueño de negocio quiere saber si puede tomar un crédito para comprar maquinaria. Le cuenta a Delphi sus ingresos, gastos y deuda actual. Delphi calcula su DSCR, le muestra tres escenarios (base, optimista, pesimista) y le dice si el crédito es viable o representa un riesgo crítico para su negocio.

### Canal
Interfaz web conversacional construida en Streamlit.

---

## 2. Plan de Implementación

### Fase 1 — Fundamentos (Sprint 1)
- Estructura del repositorio y entorno de desarrollo
- Configuracion de Supabase y tablas base
- Grafo LangGraph con nodos vacios y State definido
- Tests de infraestructura

### Fase 2 — Captura de datos (Sprint 2)
- Intake Agent: captura conversacional de datos financieros
- Validacion de inputs con Pydantic
- Persistencia de sesion en Supabase
- Tests unitarios del agente

### Fase 3 — Analisis financiero (Sprint 3)
- Scenario Agent: calculo de DSCR en tres escenarios
- Logica financiera pura en funciones helper testeables
- Visualizacion de escenarios en Streamlit

### Fase 4 — Recomendaciones y reporte (Sprint 4)
- Advisor Agent: veredicto y recomendaciones en lenguaje natural
- Generacion de reporte PDF con WeasyPrint
- Flujo end-to-end completo en Streamlit
- Tests de integracion

### Fase 5 — Seguridad y produccion (Sprint 5)
- Implementacion de guardrails en entrada y salida
- Refactorizacion y optimizacion
- Documentacion tecnica final

---

## 3. Arquitectura Tecnica

### Stack
| Componente | Tecnologia |
|---|---|
| Lenguaje | Python 3.11+ |
| Orquestacion de agentes | LangGraph (StateGraph) |
| Modelo de lenguaje | Gemini API — gemini-2.5-flash |
| Interfaz de usuario | Streamlit |
| Base de datos | Supabase (PostgreSQL) |
| Exportacion PDF | WeasyPrint |
| Gestion de entorno | python-dotenv |
| Validacion de datos | Pydantic |
| Tests | pytest |

### Grafo de agentes

```
Usuario (Streamlit)
        |
        v
  [ Intake Agent ]
  Captura datos financieros conversacionalmente.
  Extrae: ingresos, gastos, deuda, cuota mensual, sector.
        |
        v
  [ Scenario Agent ]
  Calcula DSCR en tres escenarios:
  - Base: datos actuales
  - Optimista: ingresos +20%
  - Pesimista: ingresos -20%
        |
        v
  [ Advisor Agent ]
  Genera veredicto (viable / riesgo / critico)
  y tres recomendaciones concretas en lenguaje natural.
        |
        v
  [ Reporte PDF ]
  Exporta resumen ejecutivo de una pagina.
```

### State del grafo (TypedDict)

```python
class DelphiState(TypedDict):
    mensaje_usuario: str
    historial: list[dict]
    ingresos_mensuales: float
    gastos_mensuales: float
    deuda_total: float
    cuota_mensual: float
    sector: str
    dscr_base: float
    dscr_optimista: float
    dscr_pesimista: float
    veredicto: str
    recomendaciones: list[str]
    reporte_listo: bool
```

### Logica financiera

**DSCR (Debt Service Coverage Ratio):**
```
DSCR = Flujo de caja libre / Servicio de deuda mensual
Flujo de caja libre = Ingresos mensuales - Gastos mensuales

Interpretacion:
DSCR >= 1.25  →  Viable
DSCR >= 1.00  →  Alerta
DSCR < 1.00   →  Riesgo critico
```

### Estructura del repositorio

```
repo-lab10/
├── herramientas-ia/
│   └── 01-planning/
│       ├── plantilla-brief-ia.md
│       └── protocolo-review-ia.md
├── .cursor/
│   └── agents/
│       └── qa-engineer.md
└── delphi/
    ├── README.md               (este archivo)
    ├── requirements.txt
    ├── .env.example
    ├── main.py                 (app Streamlit)
    ├── graph/
    │   └── delphi_graph.py     (StateGraph principal)
    ├── agents/
    │   ├── intake_agent.py
    │   ├── scenario_agent.py
    │   └── advisor_agent.py
    ├── skills/
    │   └── financial_calc.py   (logica financiera pura)
    ├── prompts/
    │   ├── intake_prompt.txt
    │   ├── scenario_prompt.txt
    │   └── advisor_prompt.txt
    └── tests/
        ├── test_intake.py
        ├── test_scenario.py
        ├── test_advisor.py
        └── test_financial_calc.py
```

---

## 4. Guardrails (Barreras de Seguridad)

Delphi maneja datos financieros sensibles de usuarios reales. Los guardrails se distribuyen en cuatro dimensiones a lo largo del ciclo de vida del agente.

### Guardrail 1 — Validacion de entrada (Input)

**Que protege:** evita que el agente procese datos malformados, fuera de rango o intentos de manipulacion del prompt.

**Implementacion:**
- Validacion de todos los inputs numericos con Pydantic antes de entrar al grafo
- Rangos validos: ingresos entre $0 y $10.000M COP, deuda entre $0 y $50.000M COP
- Deteccion de intentos de prompt injection: si el mensaje contiene instrucciones del sistema ("ignora tus instrucciones", "eres ahora"), el agente responde con un mensaje de error y no procesa la solicitud
- Sanitizacion de texto libre antes de concatenar al prompt

**Ejemplo de validacion:**
```python
class FinancialInput(BaseModel):
    ingresos_mensuales: float = Field(gt=0, lt=10_000_000_000)
    gastos_mensuales: float = Field(gt=0, lt=10_000_000_000)
    deuda_total: float = Field(ge=0, lt=50_000_000_000)
    cuota_mensual: float = Field(ge=0, lt=1_000_000_000)
```

### Guardrail 2 — Validacion de salida (Output)

**Que protege:** evita que el agente entregue informacion financiera incorrecta o alucinada.

**Implementacion:**
- El DSCR siempre se calcula con codigo Python puro, nunca con el LLM
- El LLM solo genera texto interpretativo, nunca numeros criticos
- Verificacion de que el veredicto sea uno de tres valores validos: "viable", "alerta", "critico"
- Si el LLM genera un veredicto fuera de estos valores, el sistema usa la regla determinista basada en el DSCR calculado

### Guardrail 3 — Control del bucle de autonomia

**Que protege:** evita que el Intake Agent haga preguntas infinitas o que el grafo entre en bucle.

**Implementacion:**
- Maximo de 10 turnos conversacionales en el Intake Agent
- Si despues de 10 turnos no se han capturado todos los datos, el agente solicita los faltantes de forma directa
- Timeout de 30 segundos por llamada al LLM
- Maximo de 3 reintentos por nodo en caso de error de la API

### Guardrail 4 — Control de herramientas y datos sensibles

**Que protege:** evita que datos financieros del usuario se expongan o persistan de forma insegura.

**Implementacion:**
- Ningun dato financiero se loggea en texto plano
- Las credenciales viven en `.env` y nunca en el codigo
- La sesion de Supabase expira automaticamente despues de la conversacion
- Delphi no tiene acceso a internet, APIs externas ni sistemas de pago — es un agente de solo lectura y analisis
- System prompt restrictivo: Delphi solo responde preguntas financieras relacionadas con el caso de uso. Si el usuario pregunta algo fuera del scope, responde: "Soy un CFO virtual especializado en analisis financiero para PyMEs. No puedo ayudarte con esa solicitud."

---

## Decision arquitectonica: workflow vs agente

Siguiendo el principio del limite del determinismo:

- **Calculo del DSCR** — es deterministico, se implementa como codigo Python puro, sin LLM
- **Captura de datos** — es ambiguo (el usuario habla en lenguaje natural, puede dar datos en cualquier orden), requiere agente
- **Generacion de recomendaciones** — requiere razonamiento contextual, requiere agente
- **Exportacion PDF** — es deterministico, se implementa con WeasyPrint sin LLM

---
