class ProductScrapDataRequestDTO:
    def __init__(self, product_data_item, title, wh_code):
        self.product_data_item = product_data_item
        self.title = title
        self.wh_code = wh_code

    def get_product_data_item(self):
        return self.product_data_item

    def get_title(self):
        return self.title

    def get_wh_code(self):
        return self.wh_code