# delphi/agents/advisor_agent.py

import json
from pathlib import Path

from google import genai
from dotenv import load_dotenv

from delphi.graph.delphi_graph import DelphiState
from delphi.skills.financial_calc import clasificar_dscr

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "advisor_prompt.txt"
_VEREDICTOS_VALIDOS = {"viable", "alerta", "critico"}


def advisor_node(state: DelphiState) -> DelphiState:
    """Genera el veredicto y tres recomendaciones para el usuario.

    Llama a gemini-2.0-flash con los escenarios calculados por scenario_node
    y pide una respuesta JSON con 'veredicto' y 'recomendaciones'.

    Guardrail (Decisión #4): si el LLM genera un veredicto fuera de
    {"viable", "alerta", "critico"}, se aplica el fallback determinista:
      clasificar_dscr(state["escenarios"]["base"]["dscr"])

    Decisión #2: si state['error'] no es None, retorna inmediatamente.
    Decisión #10: load_dotenv() y genai.Client() instanciado dentro del nodo.

    Args:
        state: Estado del grafo con 'escenarios' poblado por scenario_node.

    Returns:
        Estado actualizado con 'veredicto' y 'recomendaciones', o con
        'error' si Gemini falla o el JSON es inválido.
    """
    if state["error"] is not None:
        return state

    try:
        load_dotenv()
        import os
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

        escenarios = state["escenarios"]
        base = escenarios["base"]
        optimista = escenarios["optimista"]
        pesimista = escenarios["pesimista"]

        prompt_template = _PROMPT_PATH.read_text(encoding="utf-8")
        prompt = (
            prompt_template
            .replace("{sector}", state["sector"])
            .replace("{ingresos}", str(state["ingresos_mensuales"]))
            .replace("{gastos}", str(state["gastos_mensuales"]))
            .replace("{cuota}", str(state["cuota_mensual"]))
            .replace("{dscr_base}", str(base["dscr"]))
            .replace("{clase_base}", base["clasificacion"])
            .replace("{dscr_optimista}", str(optimista["dscr"]))
            .replace("{clase_optimista}", optimista["clasificacion"])
            .replace("{dscr_pesimista}", str(pesimista["dscr"]))
            .replace("{clase_pesimista}", pesimista["clasificacion"])
        )

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        datos = json.loads(response.text)

        veredicto = datos.get("veredicto", "")
        recomendaciones = datos.get("recomendaciones", [])

        # Guardrail: si el LLM devuelve un veredicto fuera del vocabulario
        # controlado, se usa la regla determinista basada en el DSCR base.
        if veredicto not in _VEREDICTOS_VALIDOS:
            veredicto = clasificar_dscr(base["dscr"])

        return {
            **state,
            "veredicto": veredicto,
            "recomendaciones": recomendaciones,
            "error": None,
        }

    except Exception as e:
        return {**state, "error": f"advisor_node: {e}"}
