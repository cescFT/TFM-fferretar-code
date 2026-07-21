class ProductScrapedDTO:
    def __init__(
            self,
            date,
            week_num,
            year,
            id_product,
            position,
            category,
            subcategory,
            en_category,
            en_subcategory,
            title_category_main_page,
            title_in_page_product,
            photos,
            product_name,
            en_product_name,
            quantity,
            quantity_units,
            price,
            price_units,
            pvp,
            ingredients,
            bar_code,
            is_new_arrival,
            previous_pvp,
            postal_code,
            origin
    ):
        self.date = date
        self.week_num = week_num
        self.year = year
        self.id_product = id_product
        self.position = position
        self.category = category
        self.en_category = en_category
        self.en_subcategory = en_subcategory
        self.subcategory = subcategory
        self.title_category_main_page = title_category_main_page
        self.title_in_page_product = title_in_page_product
        self.photos = photos
        self.product_name = product_name
        self.en_product_name = en_product_name
        self.quantity = quantity
        self.quantity_units = quantity_units
        self.price = price
        self.price_units = price_units
        self.pvp = pvp
        self.ingredients = ingredients
        self.bar_code = bar_code
        self.is_new_arrival = is_new_arrival
        self.previous_pvp = previous_pvp
        self.postal_code = postal_code
        self.origin = origin

    def construct_name_to_search_to_ciqual(self):
        return f"{self.en_product_name} {self.en_category} {self.en_subcategory}"

    def get_product_name(self):
        return self.product_name

    def get_insert_photos(self, row_id):
        insert_photos = []
        for photo in self.photos:
            insert_photos.append(f"INSERT INTO product_photos (product_id, photo_url) VALUES ({row_id}, '{photo}');")
        return insert_photos

    def get_insert_str(self):
        basic_insert = """
            INSERT INTO products (
                date_scraped, week_num, year, postal_code, ciqual_text_to_search, origin, id_product, position, category, subcategory,
                title_category_main_page, title_in_page_product,
                product_name, quantity, quantity_units, price, price_units,
                pvp, ingredients, bar_code, is_new_arrival, previous_pvp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        new_arrival = '0'
        if self.is_new_arrival:
            new_arrival = '1'

        previous_pvp = ''
        if self.previous_pvp:
            previous_pvp = str(self.previous_pvp)


        tuple_data = (
            self.date,
            str(self.week_num),
            self.year,
            self.postal_code,
            self.construct_name_to_search_to_ciqual(),
            self.origin,
            self.id_product,
            str(self.position),
            self.category,
            self.subcategory,
            self.title_category_main_page,
            self.title_in_page_product,
            self.product_name,
            str(self.quantity),
            self.quantity_units,
            self.price,
            self.price_units,
            self.pvp,
            self.ingredients,
            self.bar_code,
            new_arrival,
            previous_pvp
        )

        return basic_insert, tuple_data