"""
TFM: Food environment on Mercadona's supermarket

Author: Francesc Ferré Tarrés
"""

import datetime

class CategoriesAggregate:
    """
        DTO for categories aggregate data.
    """
    def __init__(
        self,
        category: str,
        subcategory: str,
        total_items: int,
        postal_code: str
    ):
        self.category = category
        self.subcategory = subcategory
        self.total_items = total_items
        self.postal_code = postal_code
        now = datetime.datetime.now()
        self.year = now.strftime("%Y")
        year_iso, week_num, day = now.isocalendar()
        self.week_num = week_num
        self.date = now.strftime("%Y-%m-%d %H:%M:%S")

    def get_insert_to_db(self):
        """
        Returns the SQL query to insert the categories aggregate data into the database.

        Returns:
            str: The SQL query.
        """
        insert = f"""
                INSERT INTO categories_counter (
                date_scraped, week_num, year,
                postal_code, category, subcategory, total_items) VALUES (
                    '{self.date}', '{self.week_num}', '{self.year}', '{self.postal_code}',
                    '{self.category}', '{self.subcategory}', {self.total_items}
                );"""
        return insert
