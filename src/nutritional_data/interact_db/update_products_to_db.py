import sqlite3
from utils.utils import get_path_sqlite_db
from interact_db.get_data_from_db import get_all_nutriments

def update_food_found_nutriments(data_to_update: list) -> None:

    new_nutriments_to_save = []
    nutriments_already_saved = []
    product_ids = []

    for product_nutritional_data_dto in data_to_update:
        nutriments = product_nutritional_data_dto.get_nutrients()
        product_ids.append(product_nutritional_data_dto.get_mercadona_id())
        for nutriment in nutriments:
            if nutriment.get_nutrient_id() is None:
                new_nutriments_to_save.append(nutriment)
            else:
                nutriments_already_saved.append(nutriment.get_nutrient_id())

    db_path = get_path_sqlite_db()

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()

        for nutriment in new_nutriments_to_save:
            cur.execute(f"""
                    insert into nutrients (nom, unitat_mesura_nutrient)
                    values (?, ?)
                    """, (nutriment.get_nutrient_name(), nutriment.get_nutrient_unit()))

        if new_nutriments_to_save:
            conn.commit()

        all_nutriments = get_all_nutriments()

        for product_nutritional_data_dto in data_to_update:
            if product_nutritional_data_dto.get_nutriscore() is not None:
                cur.execute(f"UPDATE products SET nutriscore = ? WHERE id_product = ?", (
                        product_nutritional_data_dto.get_nutriscore(),
                        product_nutritional_data_dto.get_mercadona_id()
                    )
                )

            for nutriment in product_nutritional_data_dto.get_nutrients():
                if nutriment.get_nutrient_id() is not None:
                    nutriment_id = nutriment.get_nutrient_id()
                else:
                    nutriment_id = all_nutriments[nutriment.get_nutrient_name()]

                cur.execute(f"""
                insert into producte_nutrients (product_id,producte_mercadona_id, nutrient_id, quantitat) values (?, ?, ?, ?)
                """, (
                        product_nutritional_data_dto.get_id(),
                        product_nutritional_data_dto.get_mercadona_id(),
                        nutriment_id,
                        nutriment.get_nutrient_value()
                    )
                )

        placeholder = ','.join(['?'] * len(product_ids))

        cur.execute(f"""
                update products
                set found_nutriments = 1
                where id_product IN({placeholder})
                """, product_ids)
        conn.commit()

    conn.close()