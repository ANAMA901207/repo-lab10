# delphi/main.py

import pandas as pd
import streamlit as st
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv

# Decisión #9: path explícito para que load_dotenv funcione independientemente
# del CWD desde donde se ejecuta `streamlit run delphi/main.py`.
load_dotenv(Path(__file__).parent / ".env")

from delphi.graph.delphi_graph import build_graph, initial_state

# ---------------------------------------------------------------------------
# Constantes de presentación
# ---------------------------------------------------------------------------

_COLORES = {
    "viable": "🟢",
    "alerta": "🟡",
    "critico": "🔴",
}

_ETIQUETAS = {
    "viable": "VIABLE — puede asumir la deuda con margen de seguridad",
    "alerta": "ALERTA — cubre la deuda pero sin colchón de seguridad",
    "critico": "CRÍTICO — no puede cubrir el servicio de la deuda",
}


# ---------------------------------------------------------------------------
# Caché del grafo — Decisión #8
# ---------------------------------------------------------------------------


@st.cache_resource
def _get_graph():
    """Compila el grafo una sola vez por sesión del servidor."""
    return build_graph()


# ---------------------------------------------------------------------------
# Helpers de presentación
# ---------------------------------------------------------------------------


def _fmt_cop(valor: Decimal) -> str:
    """Formatea un Decimal como pesos COP con separador de miles colombiano."""
    return f"${int(valor):,}".replace(",", ".")


def _mostrar_datos_extraidos(state: dict) -> None:
    st.subheader("📋 Datos extraídos de tu mensaje")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ingresos mensuales", _fmt_cop(state["ingresos_mensuales"]))
    col2.metric("Gastos mensuales", _fmt_cop(state["gastos_mensuales"]))
    col3.metric("Cuota mensual", _fmt_cop(state["cuota_mensual"]))
    col4.metric("Sector", state["sector"].capitalize() if state["sector"] else "—")


def _mostrar_grafico(escenarios: dict) -> None:
    st.subheader("📊 DSCR por escenario")

    # Decisión #10: conversión explícita Decimal → float antes de graficar.
    datos = pd.DataFrame(
        {"DSCR": [
            float(escenarios["base"]["dscr"]),
            float(escenarios["optimista"]["dscr"]),
            float(escenarios["pesimista"]["dscr"]),
        ]},
        index=["Base", "Optimista (+20%)", "Pesimista (-20%)"],
    )
    st.bar_chart(datos)

    # Decisión #2: referencia de umbrales como texto porque st.bar_chart
    # no soporta líneas de referencia horizontales.
    st.caption(
        "Umbrales de referencia: "
        "**≥ 1.25** → viable &nbsp;|&nbsp; "
        "**≥ 1.00** → alerta &nbsp;|&nbsp; "
        "**< 1.00** → crítico"
    )


def _mostrar_detalle_escenarios(escenarios: dict) -> None:
    st.subheader("🔢 Detalle por escenario")
    col_base, col_opt, col_pes = st.columns(3)

    for col, nombre, clave in [
        (col_base, "Base", "base"),
        (col_opt, "Optimista (+20%)", "optimista"),
        (col_pes, "Pesimista (-20%)", "pesimista"),
    ]:
        esc = escenarios[clave]
        emoji = _COLORES.get(esc["clasificacion"], "⚪")
        with col:
            st.markdown(f"**{nombre}**")
            st.markdown(f"DSCR: **{esc['dscr']}** {emoji} {esc['clasificacion'].upper()}")
            st.caption(f"Ingresos: {_fmt_cop(esc['ingresos'])}")


def _mostrar_veredicto(veredicto: str) -> None:
    st.subheader("🔍 Veredicto")
    emoji = _COLORES.get(veredicto, "⚪")
    etiqueta = _ETIQUETAS.get(veredicto, veredicto)
    mensaje = f"{emoji} **{etiqueta}**"

    if veredicto == "viable":
        st.success(mensaje)
    elif veredicto == "alerta":
        st.warning(mensaje)
    else:
        st.error(mensaje)


def _mostrar_recomendaciones(recomendaciones: list[str]) -> None:
    st.subheader("💡 Recomendaciones")
    for i, rec in enumerate(recomendaciones, start=1):
        st.markdown(f"**{i}.** {rec}")


def _mostrar_resultado(state: dict) -> None:
    """Renderiza la sección de resultados completa a partir del State final."""
    st.divider()
    _mostrar_datos_extraidos(state)
    st.divider()
    _mostrar_grafico(state["escenarios"])
    _mostrar_detalle_escenarios(state["escenarios"])
    st.divider()
    _mostrar_veredicto(state["veredicto"])
    st.divider()
    _mostrar_recomendaciones(state["recomendaciones"])


# ---------------------------------------------------------------------------
# Inicialización de session_state
# ---------------------------------------------------------------------------

if "resultado" not in st.session_state:
    st.session_state.resultado = None
if "error_msg" not in st.session_state:
    st.session_state.error_msg = None


# ---------------------------------------------------------------------------
# Layout principal
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Delphi — CFO Virtual",
    page_icon="🧠",
    layout="centered",
)

st.title("🧠 Delphi — CFO Virtual")
st.markdown(
    "Cuéntame tu situación financiera en lenguaje natural y analizaré "
    "si puedes asumir una nueva deuda. Incluye tus **ingresos mensuales**, "
    "**gastos mensuales**, **cuota mensual** del crédito que quieres tomar "
    "y el **sector** de tu negocio."
)

# ---------------------------------------------------------------------------
# Formulario de entrada
# ---------------------------------------------------------------------------

mensaje = st.text_area(
    label="Tu situación financiera",
    placeholder=(
        "Ejemplo: Tengo un negocio de comercio. Mis ingresos mensuales son "
        "10 millones de pesos, mis gastos son 7 millones y la cuota del "
        "crédito que quiero tomar sería de 2 millones al mes."
    ),
    height=140,
    key="mensaje_input",
)

analizar = st.button("Analizar mi situación", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Procesamiento al presionar el botón
# ---------------------------------------------------------------------------

if analizar:
    if not mensaje.strip():
        st.warning("Por favor describe tu situación financiera antes de continuar.")
    else:
        with st.spinner("Analizando tu situación financiera..."):
            state = initial_state(mensaje.strip())
            resultado = _get_graph().invoke(state)

        if resultado["error"] is not None:
            # Decisión #6: preservar texto para que el usuario corrija sin reiniciar.
            st.session_state.error_msg = resultado["error"]
            st.session_state.resultado = None
        else:
            st.session_state.resultado = resultado
            st.session_state.error_msg = None

# ---------------------------------------------------------------------------
# Mostrar error si existe
# ---------------------------------------------------------------------------

if st.session_state.error_msg:
    st.error(
        "No pude analizar tu mensaje. Intenta ser más específico con los "
        "valores numéricos de ingresos, gastos y cuota mensual.\n\n"
        f"_Detalle técnico: {st.session_state.error_msg}_"
    )

# ---------------------------------------------------------------------------
# Mostrar resultado si existe
# ---------------------------------------------------------------------------

if st.session_state.resultado is not None:
    _mostrar_resultado(st.session_state.resultado)

    st.divider()
    if st.button("🔄 Nueva consulta", use_container_width=True):
        # Decisión #7: limpiar session_state completo + rerun.
        st.session_state.clear()
        st.rerun()
