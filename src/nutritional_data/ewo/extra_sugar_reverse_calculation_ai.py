"""
TFM: Food environment on grocery online supermarket

Author: Francesc Ferré Tarrés
"""

import requests
import json


PROMPT = """
Actúa como experto en tecnología alimentaria, legislación alimentaria y analista de datos.
Tu tarea consiste en realizar un **cálculo nutricional inverso** de un producto para estimar la cantidad presente (en gramos por cada 100 g o ml de producto) únicamente de aquellos ingredientes considerados como "azúcar/endulzante extra OCULTO" según el criterio del sistema Ewö.

Contexto legal clave (Reglamento UE 1169/2011):
- Los azúcares simples (monosacáridos y disacáridos) YA están contabilizados legalmente en la fila "de los cuales azúcares" de la tabla nutricional.
- Los azúcares complejos o sustitutivos (maltodextrinas, dextrenas, polidextrosas, polioles, etc.) NO se contabilizan como "azúcares", sino dentro de los "hidratos de carbono totales". Estos son los ÚNICOS que constituyen "azúcar extra oculto".

Te proporcionaré los siguientes datos:
1. Valores nutricionales por 100 g o ml (hidratos de carbono totales y azúcares declarados).
2. Lista completa de ingredientes del producto (ordenados legalmente de mayor a menor peso).
3. Lista de ingredientes objetivo a analizar.

Para dar tu respuesta, debes aplicar estrictamente las siguientes **REGLAS Y CADENA DE RAZONAMIENTO**:

**PASO 1: Clasificación legal de los ingredientes objetivo**
Clasifica los ingredientes objetivo analizados según las siguientes listas estrictas:

- GRUPO A (Mono/Disacáridos declarados en la tabla nutricional):
  * Azúcar de caña / Azúcar de remolacha
  * Azúcar invertido / Azúcar líquido invertido
  * Dextrosa / Dextrosa de maíz
  * Miel
  * Sirope de agave / Jarabe de arce
  * Jarabe de glucosa / Jarabe de fructosa / Jarabe de glucosa y fructosa
  * Zumo concentrado (excluido zumo concentrado de limón)
  * Fruta seca dulce
  -> Resultado para los ingredientes de este Grupo A = 0.0g de azúcar extra (ya están contabilizados en la fila "de los cuales azúcares").

- GRUPO B (No mono/disacáridos - Azúcares Ocultos):
  * Maltodextrina / Maltodextrina de maíz
  * Dextrina
  * E1200: Polidextrosas a y n / Polidextrosas modificadas
  * E150: Caramelo / Colorante caramelo
  * Cualquier otro poliol o carbohidrato complejo no catalogado en el Grupo A.
  -> Solo los ingredientes clasificados en este Grupo B pasan al PASO 2 para ser calculados.

*Si NINGUNO de los ingredientes objetivo pertenece al Grupo B, la respuesta final de "extra_sugar" será 0.0.*

**PASO 2: Comprobación de porcentaje directo (para ingredientes del Grupo B)**
Si el ingrediente del Grupo B tiene un porcentaje explícito en la etiqueta (ejemplo: "maltodextrina (10%)"), la cantidad en gramos por 100g ES EXACTAMENTE ESE PORCENTAJE (10.0g).

**PASO 3: Acotación por orden e hidratos de carbono (para ingredientes del Grupo B)**
Si NO tiene porcentaje explícito:
- Calcula el margen de carbohidratos no azucarados: Carbohidratos_No_Azúcares = Hidratos_de_carbono_totales - Azúcares_declarados.
- Determina la posición del ingrediente en la lista respecto a los demás ingredientes colindantes para establecer un rango lógico (mínimo y máximo) que no supere el margen de carbohidratos no azucarados.

**PASO 4: Estimación final y suma**
Toma el valor medio estimado del rango del PASO 3 para cada ingrediente del Grupo B.
Suma las cantidades estimadas de todos los ingredientes del Grupo B para obtener la cifra final.

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
