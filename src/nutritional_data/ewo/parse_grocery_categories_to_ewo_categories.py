"""
TFM: Food environment on grocery online supermarket

Author: Francesc Ferré Tarrés
"""

from dto.product_nutritional_data import ProductNutrimentsDTO

def parse(product: ProductNutrimentsDTO) -> str|None:
    """
    Function that parses grocery online category, subcategory and second subcategory to EWO categories.
    Args:
        product (ProductNutrimentsDTO): Product to parse.

    Returns:
        str|None: EWO category or None if the product should be skipped.
    """

    category = product.get_category()
    subcategory = product.get_subcategory()
    second_subcategory = product.get_second_subcategory()
    alcohol = product.get_alcohol_grades()
    product_name = product.get_product_name()
    ingredients = product.get_ingredients()
    len_ingredients = len(ingredients.split(","))
    len_ingredients_y = len(ingredients.split("y"))

    print(f" * Product name: {product_name}\n")
    print(f" * Grocery online category: {category}\n")
    print(f" * Grocery online subcategory: {subcategory}\n")
    print(f" * Grocery online second subcategory: {second_subcategory}\n")
    print(f" * Alcohol: {"-" if not alcohol else alcohol}\n")
    print(f" * Ingredients: {ingredients}\n")

    calculate_ewo_category = False
    if len_ingredients > 0 or len_ingredients_y > 0:
        calculate_ewo_category = True

    if not calculate_ewo_category:
        return None

    if category == "Aceite especias y salsas":
        if subcategory == "Aceite vinagre y sal":
            if second_subcategory in ["Vinagre y otros aderezos", "Otros aceites"]:
                if alcohol:
                    return None
                return "SAVORY"
        return "SAVORY"

    if category == "Agua y refrescos":
        if subcategory != "Agua":
            return "SWEET"

    if category == "Aperitivos":
        if subcategory == "Frutos secos y fruta desecada":
            if second_subcategory in ["Frutos secos", "Fruta desecada"]:
                if len_ingredients > 0 or len_ingredients_y > 0:
                    return "SAVORY"
                return None
        return "SAVORY"

    if category == "Arroz legumbres y pasta":
        if subcategory == "Pasta y fideos" and second_subcategory in [
            "Pasta rellena",
            "Fideos orientales",
            "Lasaña y canelones"
        ]:
            return "SAVORY"

    if category == "Azúcar caramelos y chocolate":
        return "SWEET"

    if category == "Bebé":
        if subcategory == "Alimentación infantil":
            if second_subcategory in ["Tarritos salados", "Leche", "Leche en polvo"]:
                return "SAVORY"
            else:
                return "SWEET"

    if category == "Bodega":
        if alcohol:
            return None

        if subcategory == "Cerveza sin alcohol":
            return "SAVORY"

        if subcategory == "Licores" and second_subcategory == "Licores sin alcohol":
            return "SWEET"

        if subcategory == "Vino blanco" and second_subcategory == "Vinos dulces y mosto":
            return "SWEET"

    if category == "Cacao café e infusiones":
        if subcategory == "Cacao soluble y chocolate a la taza":
            return "SWEET"
        if subcategory in ["Café cápsula y monodosis", "Café molido y en grano"]:
            return "SAVORY"

        if subcategory == "Café soluble y otras bebidas":
            if second_subcategory == "Bebidas frías":
                return "SWEET"
            return "SAVORY"

    if category == "Carne":
        return "SAVORY"

    if category == "Cereales y galletas":
        return "SWEET"

    if category == "Charcutería y quesos":
        return "SAVORY"

    if category == "Congelados":
        if subcategory == "Hielo":
            return None

        if subcategory in ["Helados", "Tartas y churros"]:
            return "SWEET"

        return "SAVORY"

    if category == "Conservas caldos y cremas":
        return "SAVORY"

    if category == "Huevos leche y mantequilla":
        if subcategory in ["Leche y bebidas vegetales", "Mantequilla y margarina"]:
            if second_subcategory == "Mantequilla":
                return "SAVORY"
            return "SWEET"
        return "SAVORY"

    if category == "Marisco y pescado":
        return "SAVORY"

    if category == "Panadería y pastelería":
        if subcategory == "Bollería de horno":
            if second_subcategory == "Bollería dulce":
                return "SWEET"
            else:
                return "SAVORY"
        if subcategory in ["Bollería envasada", "Tartas y pasteles"]:
            return "SWEET"
        return "SAVORY"

    if category == "Pizzas y platos preparados":
        return "SAVORY"

    if category == "Postres y yogures":
        if subcategory == "Bífidus":
            if second_subcategory == "Bífidus de sabores":
                return "SWEET"
            else:
                return "SAVORY"

        if subcategory == "Postres de soja":
            return "SAVORY"

        if subcategory == "Yogures líquidos":
            if second_subcategory in ["Colesterol y otros", "Yogures naturales"]:
                return "SAVORY"

        return "SWEET"

    if category == "Zumos":
        return "SWEET"

    if category == "Fruta y verdura":
        if "tratado" in ingredients:
            return "SWEET"

        if "Guacamole" in product_name:
            return "SAVORY"
        if second_subcategory == "Ensalada preparada":
            return "SAVORY"

    return None
