"""
TFM: Food environment on grocery online supermarket

Author: Francesc Ferré Tarrés
"""

from dto.product_nutritional_data import ProductNutrimentsDTO

def parse(product: ProductNutrimentsDTO) -> str|None:
    """
    Function that parse online grocery category, subcategory and second subcategory to nutriscore categories.

    Args:
        product (ProductNutrimentsDTO): Product to be parsed.

    Returns:
        str|None: Category of nutriscore or None if nutriscore is not applicable.
    """

    category = product.get_category()
    subcategory = product.get_subcategory()
    second_subcategory = product.get_second_subcategory()
    alcohol = product.get_alcohol_grades()
    ingredients = product.get_ingredients()
    product_name = product.get_product_name()
    splited_ingredients = ingredients.split(",")
    splited_ingredients_y = ingredients.split("y")

    print(f" * Grocery online category: {category}\n")
    print(f" * Grocery online subcategory: {subcategory}\n")
    print(f" * Grocery online second subcategory: {second_subcategory}\n")
    print(f" * Alcohol: {"-" if not alcohol else alcohol}\n")
    print(f" * Ingredients: {ingredients}\n")

    if category == 'Aceite especias y salsas':
        if subcategory == 'Aceite vinagre y sal':
            if second_subcategory in ["Aceite de oliva", "Otros aceites"]:
                return "FATS_OILS_NUTS_SEEDS"
            elif second_subcategory == "Vinagre y otros aderezos":
                if "vinagre" in ingredients:
                    return None
                else:
                    return "GENERAL_FOOD"
        elif subcategory in ["Mayonesa, ketchup y mostaza", "Otras salsas"]:
            return "GENERAL_FOOD"
    elif category == "Agua y refrescos":
        if "coco" in ingredients:
            return "BEVERAGES"
        if "agua mineral" in product_name.lower():
            return "WATER"
        if subcategory in [
            "Isotónico y energético",
            "Refresco de cola",
            "Refresco de naranja y de limón",
            "Tónica y bitter"
        ]:
            return "BEVERAGES"
        elif subcategory == 'Refresco de té y sin gas':
            if second_subcategory == "Té":
                if len(splited_ingredients) > 0 or len(splited_ingredients_y) > 0:
                    return "BEVERAGES"
                else:
                    return None
            elif second_subcategory == "Otros refrescos sin gas":
                return "BEVERAGES"
    elif category == "Aperitivos":
        if subcategory == "Aceitunas y encurtidos":
            return "GENERAL_FOOD"
        if subcategory == "Frutos secos y fruta desecada":
            if second_subcategory == "Fruta desecada":
                return "GENERAL_FOOD"
            return "FATS_OILS_NUTS_SEEDS"
        if subcategory == "Patatas fritas y snacks":
            return "GENERAL_FOOD"
    elif category == "Arroz legumbres y pasta":
        if subcategory == "Arroz":
            if "cocido" in ingredients or \
                "cocida" in ingredients or \
                "cous cous"in product_name.lower():
                return "GENERAL_FOOD"
        if subcategory == "Legumbres":
            if len(splited_ingredients) > 1 or len(splited_ingredients_y) > 1:
                return "GENERAL_FOOD"
        if subcategory == "Pasta y fideos" and second_subcategory in ["Pasta rellena", "Fideos orientales"]:
            return "GENERAL_FOOD"
    elif category == "Azúcar caramelos y chocolate":
        if subcategory in ["Chicles y caramelos","Chocolate","Golosinas"]:
            return "GENERAL_FOOD"
        elif subcategory == "Mermelada y miel":
            if second_subcategory in ["Mermelada", "Confitura y otros"]:
                return "GENERAL_FOOD"
    elif category == "Bodega":
        if subcategory in [
            "Cerveza",
            "Licores",
            "Sidra y cava",
            "Tinto de verano y sangría",
            "Vino blanco",
            "Vino lambrusco y espumoso",
            "Vino rosado",
            "Vino tinto"
        ]:
            if second_subcategory == "Licores sin alcohol":
                return "BEVERAGES"
            if alcohol > 1.2:
                return None
    elif category == "Cacao café e infusiones":
        if subcategory == "Cacao soluble y chocolate a la taza":
            return "GENERAL_FOOD"
    elif category == "Carne":
        if subcategory in ["Arreglos", "Carne congelada", "Hamburguesa y picadas", "Empanados y elaborados"]:
            return check_if_is_red_meal(ingredients)
        elif subcategory in ["Cerdo", "Embutido", "Vacuno"]:
            return "RED_MEAT"
        elif subcategory == "Conejo y cordero":
            if second_subcategory == "Conejo":
                return "GENERAL_FOOD"
            elif second_subcategory == "Cordero":
                return "RED_MEAT"
        else:
            return "GENERAL_FOOD"
    elif category == "Cereales y galletas":
        return "GENERAL_FOOD"
    elif category == "Charcutería y quesos":
        if subcategory == "Aves y jamón cocido":
            if second_subcategory == "Pavo y otros":
                return "GENERAL_FOOD"
            elif second_subcategory == "Jamón cocido":
                return "RED_MEAT"
        elif subcategory == "Paté y sobrasada":
            if second_subcategory == "Paté":
                return "GENERAL_FOOD"
            elif second_subcategory == "Sobrasada":
                return "RED_MEAT"
        elif "queso" in subcategory.lower():
            return "CHEESE"
        else:
            return "RED_MEAT"
    elif category == "Congelados":
        if subcategory in [
            "Arroz y pasta",
            "Fruta y verdura",
            "Helados",
            "Marisco",
            "Pizzas",
            "Rebozados",
            "Tartas y churros"
        ]:
            if second_subcategory in ["Carne rebozada", "Carne"]:
                return check_if_is_red_meal(ingredients)
            return "GENERAL_FOOD"
    elif category == "Conservas caldos y cremas":
        return "GENERAL_FOOD"
    elif category == "Fruta y verdura":
        if subcategory == "Lechuga y ensalada preparada":
            if second_subcategory == "Ensalada preparada":
                return "GENERAL_FOOD"
    elif category == "Huevos leche y mantequilla":
        if subcategory == "Leche y bebidas vegetales":
            if second_subcategory in [
                "Leche semidesnatada",
                "Leche desnatada",
                "Leche entera",
                "Bebidas vegetales",
                "Batidos"
            ]:
                return "BEVERAGES"
            elif second_subcategory == "Leche condensada y otros":
                return "GENERAL_FOOD"
        elif subcategory == "Mantequilla y margarina":
            return "FATS_OILS_NUTS_SEEDS"
    elif category == "Marisco y pescado":
        if subcategory in ["Marisco", "Pescado congelado", "Salazones y ahumados"]:
            return "GENERAL_FOOD"
    elif category == "Panadería y pastelería":
        if subcategory in [
            "Bollería de horno",
            "Bollería envasada",
            "Pan de horno",
            "Pan de molde y otras especialidades",
            "Picos, rosquilletas y picatostes",
            "Tartas y pasteles"
        ]:
            return "GENERAL_FOOD"
        elif subcategory == "Harina y preparado repostería":
            if second_subcategory == "Masas":
                return "GENERAL_FOOD"
        elif subcategory == "Pan tostado y rallado":
            if second_subcategory in ["Pan tostado", "Crackers y tartaletas"]:
                return "GENERAL_FOOD"
    elif category == "Pizzas y platos preparados":
        if subcategory in [
            "Listo para Comer",
            "Pizzas",
            "Platos preparados fríos"
        ]:
            return "GENERAL_FOOD"
        elif subcategory == "Platos preparados calientes":
            if second_subcategory == "Carne":
                return check_if_is_red_meal(ingredients)
            else:
                return "GENERAL_FOOD"
    elif category == "Postres y yogures":
        if subcategory in [
            "Bífidus",
            "Flan y natillas",
            "Postres de soja",
            "Yogures desnatados",
            "Yogures griegos",
            "Yogures líquidos"
        ]:
            return "GENERAL_FOOD"
        elif subcategory == "Gelatina y otros postres":
            if second_subcategory == "Gelatina":
                return None
            elif second_subcategory == "Otros postres":
                return "GENERAL_FOOD"
    elif category == "Zumos":
        return "BEVERAGES"

    return None


def check_if_is_red_meal(ingredients: str) -> str:
    if ingredients and 'ternera' in ingredients or \
            'cerdo' in ingredients or \
            'cordero' in ingredients:
        return "RED_MEAT"
    else:
        return "GENERAL_FOOD"