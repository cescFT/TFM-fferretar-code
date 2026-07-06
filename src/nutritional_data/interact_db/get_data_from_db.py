import sqlite3
from utils.utils import get_path_sqlite_db


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
                select p.id, p.id_product, p.category, p.subcategory, p.product_name
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

            result.append({
                'id': product[0],
                'id_product': product[1],
                'category': product[2],
                'subcategory': product[3],
                'product_name': product[4],
                'photo_urls': photos
            })

    conn.close()

    return result