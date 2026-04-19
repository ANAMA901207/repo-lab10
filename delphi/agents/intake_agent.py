# delphi/agents/intake_agent.py

import json
from decimal import Decimal
from pathlib import Path

from google import genai
from dotenv import load_dotenv
from pydantic import BaseModel, field_validator

from delphi.graph.delphi_graph import DelphiState

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "intake_prompt.txt"


class _FinancialData(BaseModel):
    """Esquema Pydantic para validar la respuesta JSON de Gemini."""

    ingresos_mensuales: Decimal
    gastos_mensuales: Decimal
    deuda_total: Decimal
    cuota_mensual: Decimal
    sector: str

    @field_validator("sector")
    @classmethod
    def sector_no_vacio(cls, v: str) -> str:
        return v.strip() if v.strip() else "no especificado"


def intake_node(state: DelphiState) -> DelphiState:
    """Extrae los datos financieros del mensaje del usuario usando Gemini.

    Flujo:
      1. Carga el prompt desde prompts/intake_prompt.txt
      2. Llama a gemini-2.0-flash con el mensaje del usuario
      3. Parsea la respuesta como JSON con json.loads()
      4. Valida los campos requeridos con Pydantic (_FinancialData)
      5. Escribe los valores en el State como Decimal

    Decisión #2: si state['error'] no es None, retorna sin ejecutar.
    Decisión #10: load_dotenv() y genai.Client() se instancian dentro del nodo.
    Decisión #11: single-shot — captura todo en un turno.

    Args:
        state: Estado del grafo con mensaje_usuario poblado.

    Returns:
        Estado actualizado con los 5 campos financieros, o con 'error'
        si Gemini falla, el JSON es inválido o la validación falla.
    """
    if state["error"] is not None:
        return state

    try:
        load_dotenv()
        import os
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

        prompt_template = _PROMPT_PATH.read_text(encoding="utf-8")
        prompt = prompt_template.replace("{mensaje}", state["mensaje_usuario"])

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )

        datos = _FinancialData.model_validate(json.loads(response.text))

        return {
            **state,
            "ingresos_mensuales": datos.ingresos_mensuales,
            "gastos_mensuales": datos.gastos_mensuales,
            "deuda_total": datos.deuda_total,
            "cuota_mensual": datos.cuota_mensual,
            "sector": datos.sector,
            "error": None,
        }

    except Exception as e:
        return {**state, "error": f"intake_node: {e}"}
