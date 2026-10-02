"""
TFM: Food environment on grocery online supermarket

Author: Francesc Ferré Tarrés
"""

import requests
import json


PROMPT = """
Actúa como experto en tecnología alimentaria, legislación alimentaria y analista de datos.
Tu tarea consiste en realizar un **cálculo nutricional inverso** de un producto para estimar
la cantidad presente (en gramos por cada 100 g o ml de producto) de uno o varios ingredientes específicos
considerados como "azúcar/endulzante extra".

Te proporcionaré los siguientes datos:
1. Valores nutricionales por 100 g o ml (hidratos de carbono totales y azúcares declarados).
2. Lista completa de ingredientes del producto (ordenados legalmente de mayor a menor peso).
3. Lista de ingredientes objetivo a analizar.

Para dar tu respuesta, debes aplicar estrictamente las siguientes **REGLAS DE PRIORIDAD Y CADENA DE RAZONAMIENTO**:

--- REGLAS DE ORO (INVIOLABLES) ---
REGLA 1 (DECLARACIÓN DIRECTA): Si el ingrediente objetivo tiene un porcentaje explícito en la etiqueta,
 la cantidad en gramos por 100g ES EXACTAMENTE ESE PORCENTAJE (ejemplo: 12.0g). NO PUEDE SER MAYOR NI MENOR.

REGLA 2 (ORDEN Y PORCENTAJES ADYACENTES): Si el ingrediente objetivo NO tiene porcentaje explícito, su cantidad DEBE SER ESTRICTAMENTE MENOR que el ingrediente anterior y MAYOR que el ingrediente posterior.
Si hay ingredientes colindantes con porcentaje (ej: "almendra (66%)" ... ingrediente X ... "miel (12%)"), el ingrediente X debe estar dentro de ese rango (entre 12g y 66g).

REGLA 3 (TECHO NUTRICIONAL): La suma total de los ingredientes estimados jamás puede superar los hidratos de carbono totales
declarados en la tabla nutricional, ni el peso total pendiente de la fórmula del producto.
------------------------------------

**PASO 1: Comprobación de porcentaje directo (Regla 1)**
Analiza si el ingrediente objetivo tiene un porcentaje numérico escrito entre paréntesis.
- Si LO TIENE: Asigna directamente ese porcentaje como el valor en gramos por 100g.
- Si NO LO TIENE: Procede al PASO 2.

**PASO 2: Acotación por orden e hidratos de carbono (Regla 2 y 3)**
- Extrae los hidratos de carbono totales y los azúcares declarados.
- Determina el rango de peso mínimo y máximo posible para el ingrediente según su posición exacta en la lista
respecto a los demás ingredientes declarados.

**PASO 3: Estimación final**
Si no hay porcentaje directo, toma el valor medio estimado dentro del rango lógico calculado en el PASO 2.

Devuelve EXCLUSIVAMENTE el objeto JSON final.

Formato de salida esperado:
{
  "extra_sugar": float
}

Estos son los datos del producto:
- Valores nutricionales: @@nutritional_values@@
- Lista de ingredientes del producto: @@ingredients@@
- Ingredientes objetivo a analizar: @@target_ingredients@@
"""

def reverse_calculation_extra_sugar(
    ingredients: str,
    sugars_total: float,
    carbohydrate_total: float,
    ingredient_names: str
) -> float:
    """
    Function that calculates extra sugar of specific ingredient which is not declared on total sugars (g). It uses
    AI, as requested by Ewö team to make reverse calculation of extra sugar to add in declared total sugars.
    Args:
        ingredients (str): List of ingredients.
        sugars_total (float): Total sugars declared in the product (g).
        carbohydrate_total (float): Total carbohydrates declared in the product (g).
        ingredient_names (str): Name of the ingredients for which extra sugar is calculated.

    Returns:
        float: Extra sugar calculated for the ingredient (g).
    """

    prompt = PROMPT.replace(
        "@@nutritional_values@@",
        "Hidratos de carbono "+ str(carbohydrate_total) +
        "g de los cuales "+ str(sugars_total)  + "g son de azúcares")

    prompt = prompt.replace("@@ingredients@@", ingredients)
    prompt = prompt.replace("@@target_ingredients@@", ingredient_names)

    print(f"Request sent to Ollama (llama3.2 model) for calculating extra sugar of ingredients {ingredient_names} ...")

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "llama3.2",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "format": {
                "type": "object",
                "properties": {
                    "extra_sugar": {
                        "type": "number"
                    }
                },
                "required": ["extra_sugar"]
            },
            "stream": False
        }
    )

    try:
        result = json.loads(response.json()["message"]["content"])['extra_sugar']
        print("Extra sugar calculated for " + ingredient_names + " is " + str(result) + "g")
    except Exception as e:
        print("Error parsing response: " + str(e))
        result = 0

    return result
