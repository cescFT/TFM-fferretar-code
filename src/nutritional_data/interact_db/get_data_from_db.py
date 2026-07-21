import sqlite3
from utils.utils import get_path_sqlite_db
from ciqual import requests as request_to_ciqual
from dto.gemini_model_data import GeminiModelDTO

def get_gemini_models() -> list:
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


def get_products_without_nutritional_data(limit: int) -> list:

    result = []
    db_path = get_path_sqlite_db()
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("""
                select p.id, p.id_product, p.category, p.subcategory, p.product_name, p.origin, p.ciqual_text_to_search
                from products p
                inner join product_photos ph on ph.product_id = p.id
                left join producte_nutrients pn on pn.producte_mercadona_id = p.id_product
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
                print("La petició a ciqual ha fallat: ", e)

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