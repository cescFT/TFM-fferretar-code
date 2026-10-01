"""
TFM: Food environment on grocery online supermarket

Author: Francesc Ferré Tarrés
"""

import requests
import json


PROMPT = """
Actúa como experto en tecnología alimentaria, legislación alimentaria y analista de datos.
Tu tarea consiste en realizar un **cálculo nutricional inverso** de un producto para estimar
qué cantidad, en gramos, de un ingrediente específico constituye el azúcar añadido por cada 100 g o ml del producto.

Te proporcionaré los siguientes datos:
1. Valores nutricionales por cada 100 g o ml (especialmente hidratos de carbono y azúcares totales).
2. Lista de ingredientes (que, por ley, se ordenan de mayor a menor según su peso).
3. El ingrediente concreto que quiero que analices.

Para dar tu respuesta, debes seguir estrictamente estos pasos de la **cadena de razonamiento**:

**PASO 1: Análisis de la tabla nutricional**
Extrae los azúcares totales por cada 100 g. Este es tu límite máximo absoluto (el 100 % del azúcar del producto).

**PASO 2: Identificación de las fuentes de azúcar**
Analiza la lista de ingredientes y clasifícalos en dos categorías:
- Fuentes de azúcar intrínsecas (p. ej., fruta, leche/lactosa, etc.). Calcula su porcentaje medio de azúcar natural.
- Fuentes de azúcares añadidos (p. ej., sacarosa, jarabe de glucosa, miel, dextrosa, etc.).

**PASO 3: Razonamiento por peso relativo (orden de los ingredientes)**
Utiliza la norma de etiquetado de los alimentos: los ingredientes se enumeran en orden descendente por peso.
- Si el ingrediente X aparece antes que el ingrediente Y, X > Y en gramos.
- Si se indican porcentajes para un ingrediente,
 utilízalos como puntos de referencia matemáticos para limitar el peso máximo y mínimo
  de los ingredientes restantes.

**PASO 4: Cálculo de los límites y estimación**
Resta los azúcares estimados procedentes de fuentes naturales (si los hay) del total de azúcares.
El resultado es el total de azúcares añadidos.
Distribuye estos azúcares añadidos entre los ingredientes edulcorantes
de acuerdo con su orden en la lista de ingredientes.

**PASO 5: Conclusión**
Indica claramente la estimación final. Si no se puede obtener una cifra matemática exacta por falta de porcentajes
explícitos en el etiquetado, realiza la estimación razonada basada en los rangos
y devuelve el valor medio estimado (float redondeado a un decimal).

Formato de salida esperado: {"extra_sugar": float}

Estos son los datos del producto:
- Valores nutricionales: @@nutritional_values@@
- Ingredientes: @@ingredients@@
- Ingrediente objectivo: @@ingredient_objective@@
"""


def reverse_calculation_extra_sugar(
    ingredients: str,
    sugars_total: float,
    carbohydrate_total: float,
    ingredient_name: str
) -> float:
    """
    Function that calculates extra sugar of specific ingredient which is not declared on total sugars (g). It uses
    AI, as requested by Ewö team to make reverse calculation of extra sugar to add in declared total sugars.
    Args:
        ingredients (str): List of ingredients.
        sugars_total (float): Total sugars declared in the product (g).
        carbohydrate_total (float): Total carbohydrates declared in the product (g).
        ingredient_name (str): Name of the ingredient for which extra sugar is calculated.

    Returns:
        float: Extra sugar calculated for the ingredient (g).
    """

    prompt = PROMPT.replace(
        "@@nutritional_values@@",
        "Hidratos de carbono "+ str(carbohydrate_total) +
        "g de los cuales "+ str(sugars_total)  + "g son de azúcares")

    prompt = prompt.replace("@@ingredients@@", ingredients)
    prompt = prompt.replace("@@ingredient_objective@@", ingredient_name)

    print(f"Request sent to Ollama (llama3.2 model) for calculating extra sugar of ingredient {ingredient_name} ...")

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
        print("Extra sugar calculated for " + ingredient_name + " is " + str(result) + "g")
    except Exception as e:
        print("Error parsing response: " + str(e))
        result = 0

    return result
