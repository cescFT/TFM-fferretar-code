"""
TFM: Food environment on Mercadona's supermarket

Author: Francesc Ferré Tarrés
"""

class ProductScrapDataRequestDTO:
    """
    DTO class for requests data to scrap.
    """
    def __init__(self, product_data_item: dict, title: str, wh_code: str):
        self.product_data_item = product_data_item
        self.title = title
        self.wh_code = wh_code

    def get_product_data_item(self) -> dict:
        """
        Function get product data item.

        Args:
            None.

        Returns:
             dict: Product data for scrap info.
        """

        return self.product_data_item

    def get_title(self) -> str:
        """
        Function get product title.

        Args:
            None.

        Returns:
             str: Title banner.
        """

        return self.title

    def get_wh_code(self) -> str:
        """
        Function get product warehouse code of mercadona supermarket depending on postal code.

        Args:
            None.

        Returns:
             str: Warehouse code of mercadona supermarket.
        """

        return self.wh_code
