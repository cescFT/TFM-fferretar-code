"""
TFM: Food environment on grocery online supermarket

Author: Francesc Ferré Tarrés
"""

from utils.utils import (
    get_path_sqlite_db,
    match_nutritional_data_with_each_product,
    match_product_data_with_certifications_each_product)
from ciqual import requests as request_to_ciqual
from dto.gemini_model_data import GeminiModelDTO
from constants.constants_variables import constants_variables_getter

import sqlite3

NO_DATA_NUTRIMENTS = constants_variables_getter("NUTRIMENT_NO_DATA")
CERTIFICATIONS_NO_DATA = constants_variables_getter("CERTIFICATIONS_NO_DATA")

def retrieve_product_data_from_grocery_id(grocery_id: str) -> dict|None:
    """
    Retrieve product data using grocery online id.

    Args:
        grocery_id (str): Grocery online id.

    Returns:
        dict|None: All data about the product.
    """

    db_path = get_path_sqlite_db()
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("""
                    SELECT origin, found_nutriments,  nutriscore,  planetscore,
                           ciqual_text, ciqual_id, ewo_ultra_processed_punctuation
                    from products p
                    where p.id_product = ?
                        group by p.id_product
                    """, (grocery_id,))
        response = cur.fetchone()

    conn.close()

    if not response:
        return None

    return {
        'origin': response[0],
        'found_nutriments': response[1] == 1,
        'nutriscore': response[2],
        'planetscore': response[3],
        'ciqual_text': response[4],
        'ciqual_id': response[5],
        'ewo_ultra_processed_punctuation': response[6],
    }

def get_gemini_models() -> list:
    """
    Returns all gemini models availables ordered by id.

    Args:
        None.

    Returns:
        list: List of gemini models.
    """

    db_path = get_path_sqlite_db()
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT model_name, (unixepoch() - last_petition) / 3600 as hours_since_last_petition, is_blocked
            FROM gemini_models
            order by id
            """)
        response = cur.fetchall()

    conn.close()

    response_dto = []
    for gemini_data in response:
        response_dto.append(GeminiModelDTO(gemini_data[0], gemini_data[1], gemini_data[2]))

    return response_dto

def get_all_certifications() -> dict:
    """
    Gets all product certifications available into database.

    Args:
        None.

    Returns:
        dict: Dictionary of certifications.
    """

    to_return = {}
    db_path = get_path_sqlite_db()

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()

        query = "SELECT id, certification_name FROM certifications"

        cur.execute(query)

        response = cur.fetchall()

        for certification in response:
            to_return[certification[1]] = certification[0]
    conn.close()

    return to_return

def get_all_nutriments() -> dict:
    """
    Gets all nutriments available in database.

    Args:
        None.

    Returns:
        dict: Dictionary indexed by id and value is name.
    """

    to_return = {}
    db_path = get_path_sqlite_db()

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()

        query = "SELECT id, nom, unitat_mesura_nutrient FROM nutrients"

        cur.execute(query)

        response = cur.fetchall()

        for nutrient in response:
            to_return[nutrient[1]] = nutrient[0]

    conn.close()

    return to_return

def get_types_of_certifications(special_certifications_ids: list) -> dict:
    """
    Get types of certifications that are not special certifications.

    Args:
        special_certifications_ids (list): List of special certifications which are no needed.

    Returns:
        dict: Dictionary indexed by id and as value is certification name.
    """

    to_return = {}
    db_path = get_path_sqlite_db()

    placeholders = ", ".join(["?"] * len(special_certifications_ids))

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            f"SELECT id, certification_name FROM certifications where id not in({placeholders})",
            special_certifications_ids
        )
        response = cur.fetchall()

        for nutrient in response:
            to_return[nutrient[1]] = nutrient[0]

    conn.close()

    return to_return


def get_types_of_nutriments(special_nutriments_ids: list) -> dict:
    """
    Gets all nutriments without special nutriments not no get.

    Args:
        special_nutriments_ids (list): List of special nutriments ids not to get.

    Returns:
        dict: Dictionary where id is the index and value is the name.
    """

    to_return = {}
    db_path = get_path_sqlite_db()

    placeholders = ", ".join(["?"] * len(special_nutriments_ids))

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            f"SELECT id, nom FROM nutrients where id not in({placeholders})",
            special_nutriments_ids
        )
        response = cur.fetchall()

        for nutrient in response:
            to_return[nutrient[1]] = nutrient[0]

    conn.close()

    return to_return

def get_nutriments_of_specific_products(grocery_ids: list) -> dict:
    """
    Function to retrieve nutriments of specific products by grocery id

    Args:
        grocery_ids (list): List of grocery ids products.

    Returns:
        dict: Dictionary with grocery_id as key and list of nutriments as value
    """

    db_path = get_path_sqlite_db()
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        placeholders = ", ".join(["?"] * len(grocery_ids))
        cur.execute(f"""
                select pn.product_grocery_id, n.id as id_nutrient, n.nom, pn.quantitat, n.unitat_mesura_nutrient
                from producte_nutrients pn
                inner join nutrients n on n.id = pn.nutrient_id
                where
                    pn.product_grocery_id in ({placeholders})
                """, grocery_ids)

        nutriments = cur.fetchall()
        nutriments_indexed_by_grocery_id = {}
        for nutriment in nutriments:
            grocery_product_id = nutriment[0]
            nutriment_id = nutriment[1]
            if not grocery_product_id in nutriments_indexed_by_grocery_id:
                nutriments_indexed_by_grocery_id[grocery_product_id] = []

            if nutriment_id == int(NO_DATA_NUTRIMENTS):
                continue

            nutriments_indexed_by_grocery_id[grocery_product_id].append({
                'id_nutriment': nutriment_id,
                'nutriment_name': nutriment[2],
                'quantity': nutriment[3],
                'units': nutriment[4]
            })

    conn.close()
    return nutriments_indexed_by_grocery_id

def get_certifications_of_specific_products(grocery_ids: list) -> dict:
    """
    Function that gets certification information of specific products by grocery ids.
    Args:
        grocery_ids (list): List of grocery IDs.

    Returns:
        dict: Certifications indexed by grocery ID.
    """

    db_path = get_path_sqlite_db()
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(f"""
            select c.id, c.certification_name, pc.product_id
            from product_certifications pc
            inner join certifications c on pc.certification_id = c.id
            where pc.product_id in ({','.join(['?'] * len(grocery_ids))})
        """, grocery_ids)

        certifications = cur.fetchall()

        certifications_indexed_by_grocery_id = {}
        for certification in certifications:
            certification_id = certification[0]
            certification_name = certification[1]
            grocery_product_id = certification[2]

            if grocery_product_id not in certifications_indexed_by_grocery_id:
                certifications_indexed_by_grocery_id[grocery_product_id] = []

            if certification_id == int(CERTIFICATIONS_NO_DATA):
                continue

            certifications_indexed_by_grocery_id[grocery_product_id].append({
                'id': certification_id,
                'certification_name': certification_name
            })

    conn.close()
    return certifications_indexed_by_grocery_id

def get_products_without_ewo_ultraprocessed_qualification(limit: int) -> list:
    """
    Function that gets products without ultraprocessed qualification.

    Args:
        limit (int): Number limit of products to be find.

    Returns:
        list: List of products without ultraprocessed qualification.
    """

    response = []

    db_path = get_path_sqlite_db()
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("""
                    select p.id,
                           p.id_product,
                           p.category,
                           p.subcategory,
                           p.second_subcategory,
                           p.product_name,
                           p.ingredients,
                           p.alcohol_grades
                    from products p
                    where p.ewo_ultra_processed_punctuation is null
                      and p.found_nutriments = 1
                    group by p.id_product limit ?
                    """, (limit,))

        products = cur.fetchall()

        if not products:
            return response

        grocery_products_ids = []
        for product in products:
            response.append({
                'id': product[0],
                'id_product': product[1],
                'category': product[2],
                'subcategory': product[3],
                'second_subcategory': product[4],
                'product_name': product[5],
                'ingredients': product[6],
                'alcohol_grades': product[7]
            })
            grocery_products_ids.append(product[1])

        nutriments = get_nutriments_of_specific_products(grocery_products_ids)
        certifications = get_certifications_of_specific_products(grocery_products_ids)
        response = match_nutritional_data_with_each_product(nutriments, response)
        response = match_product_data_with_certifications_each_product(response, certifications)

    conn.close()

    return response

def get_products_without_nutriscore(limit: int) -> list:
    """
    Get products without nutriscore limited by parameter with all
    nutriment data mandatory to calculate nutriscore.

    Args:
        limit (int): Number limit of products to be find.

    Returns:
        list: List of products without nutriscore.
    """

    result = []
    data_to_return = []
    db_path = get_path_sqlite_db()
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("""
                    select p.id,
                           p.id_product,
                           p.category,
                           p.subcategory,
                           p.second_subcategory,
                           p.product_name,
                           p.ingredients,
                           p.alcohol_grades
                    from products p
                    where 
                        p.nutriscore is null and
                        p.found_nutriments = 1
                    group by p.id_product
                    limit ?
                    """, (limit,))

        products = cur.fetchall()

        if not products:
            return result

        grocery_products_ids = []

        for product in products:
            result.append({
                'id': product[0],
                'id_product': product[1],
                'category': product[2],
                'subcategory': product[3],
                'second_subcategory': product[4],
                'product_name': product[5],
                'ingredients': product[6],
                'alcohol_grades': product[7]
            })
            grocery_products_ids.append(product[1])

        nutriments_indexed_by_grocery_id = get_nutriments_of_specific_products(grocery_products_ids)
        data_to_return = match_nutritional_data_with_each_product(nutriments_indexed_by_grocery_id, result)

    conn.close()

    return data_to_return

def get_products_without_nutritional_data(limit: int) -> list:
    """
    Get products without nutritional data limited by paramter.

    Args:
        limit (int): Limit of products to return.

    Returns:
        list: List of products without nutritional data.
    """

    result = []
    db_path = get_path_sqlite_db()
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("""
                select p.id, p.id_product, p.category, p.subcategory, p.product_name, p.origin, p.ciqual_text_to_search
                from products p
                inner join product_photos ph on ph.product_id = p.id
                left join producte_nutrients pn on pn.product_grocery_id = p.id_product
                where 
                    p.found_nutriments = 0 and
                    pn.nutrient_id is null
                group by p.id_product
                limit ?
        """, (limit,))

        products = cur.fetchall()

        if not products:
            return result

        products_indexed_by_id = {product[0]: product for product in products}

        ids = list(products_indexed_by_id.keys())
        placeholders = ", ".join(["?"] * len(ids))

        cur.execute(f"""
            SELECT photo_url, product_id
            FROM product_photos
            WHERE product_id IN ({placeholders})
        """, ids)

        photos = cur.fetchall()

        photos_data = {}
        for photo in photos:
            product_id = photo[1]
            if product_id not in photos_data:
                photos_data[product_id] = []
                photos_data[product_id].append(photo[0])
            else:
                photos_data[product_id].append(photo[0])

        for product in products:
            photos = photos_data.get(product[0], [])
            if not photos:
                continue

            try:
                ciqual_response = request_to_ciqual.get_results(product[6])
            except Exception as e:
                print("Ciqual request failed: ", e)

            result.append({
                'id': product[0],
                'id_product': product[1],
                'category': product[2],
                'subcategory': product[3],
                'product_name': product[4],
                'photo_urls': photos,
                'origin': product[5],
                'ciqual_text_to_search': product[6],
                'ciqual_possible_responses': ciqual_response
            })

    conn.close()

    return result
