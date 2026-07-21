import sqlite3
from utils.utils import get_path_sqlite_db
from interact_db.get_data_from_db import get_all_nutriments, get_all_certifications

def update_food_found_nutriments(data_to_update: list) -> None:

    new_nutriments_to_save = []
    new_certifications_to_save = []
    nutriments_already_saved = []
    certifications_already_saved = []
    product_ids = []

    for product_nutritional_data_dto in data_to_update:
        nutriments = product_nutritional_data_dto.get_nutrients()
        product_ids.append(product_nutritional_data_dto.get_mercadona_id())
        for nutriment in nutriments:
            if nutriment.get_nutrient_id() is None:
                new_nutriments_to_save.append(nutriment)
            else:
                nutriments_already_saved.append(nutriment.get_nutrient_id())

        for certification in product_nutritional_data_dto.get_certifications():
            if certification.get_certification_id() is None:
                new_certifications_to_save.append(certification)
            else:
                certifications_already_saved.append(certification.get_certification_id())


    unique_new_nutriments_to_save = {}
    for nutriment in new_nutriments_to_save:
        if nutriment.get_nutrient_name() not in unique_new_nutriments_to_save:
            unique_new_nutriments_to_save[nutriment.get_nutrient_name()] = nutriment.get_nutrient_unit()

    unique_certifications_to_save = {}
    for certification in new_certifications_to_save:
        if certification.get_certification_name() not in unique_certifications_to_save:
            unique_certifications_to_save[certification.get_certification_name()] = certification.get_certification_id()

    db_path = get_path_sqlite_db()

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()

        for nutriment_name, unit in unique_new_nutriments_to_save.items():
            cur.execute(f"""
                    insert into nutrients (nom, unitat_mesura_nutrient)
                    values (?, ?)
                    """, (nutriment_name, unit))

        if unique_new_nutriments_to_save:
            conn.commit()

        all_nutriments = get_all_nutriments()

        for certification_name, certification_id in unique_certifications_to_save.items():
            cur.execute(f"""
                    insert into certifications (certification_name)
                    values (?)
                    """, (certification_name,))

        if unique_certifications_to_save:
            conn.commit()

        all_certifications = get_all_certifications()

        for product_nutritional_data_dto in data_to_update:
            if product_nutritional_data_dto.get_nutriscore() is not None:
                cur.execute(f"UPDATE products SET nutriscore = ? WHERE id_product = ?", (
                        product_nutritional_data_dto.get_nutriscore(),
                        product_nutritional_data_dto.get_mercadona_id()
                    )
                )

            if not product_nutritional_data_dto.get_origin() and \
                product_nutritional_data_dto.get_origin_from_gemini() is not None:
                cur.execute(f"UPDATE products SET origin = ? WHERE id_product = ?", (
                        product_nutritional_data_dto.get_origin_from_gemini(),
                        product_nutritional_data_dto.get_mercadona_id()
                    )
                )

            if product_nutritional_data_dto.get_ciqual_response() is not None:
                cur.execute(f"UPDATE products SET ciqual_text = ?, ciqual_id = ? WHERE id_product = ?", (
                    product_nutritional_data_dto.get_ciqual_response().get_text(),
                    product_nutritional_data_dto.get_ciqual_response().get_id(),
                    product_nutritional_data_dto.get_mercadona_id()
                ))

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

            for certification in product_nutritional_data_dto.get_certifications():
                if certification.get_certification_id() is not None:
                    certification_id = certification.get_certification_id()
                else:
                    certification_id = all_certifications[certification.get_certification_name()]

                cur.execute(f"""
                                insert into product_certifications (product_id,certification_id) values (?, ?)
                                """, (
                        product_nutritional_data_dto.get_mercadona_id(),
                        certification_id
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