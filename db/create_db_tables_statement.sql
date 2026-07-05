DROP TABLE IF EXISTS "product_photos";
DROP TABLE IF EXISTS "products";

CREATE TABLE "products" (
	"id"	INTEGER NOT NULL,
	"date_scraped"	TEXT NOT NULL,
    "week_num"      TEXT NOT NULL,
    "year"          TEXT NOT NULL,
	"postal_code"	TEXT NOT NULL,
	"found_nutriments"	INTEGER NOT NULL DEFAULT 0,
	"id_product"	INTEGER NOT NULL,
	"position"	INTEGER NOT NULL,
	"category"	TEXT NOT NULL,
	"subcategory"	TEXT NOT NULL,
	"title_category_main_page"	TEXT NOT NULL,
	"title_in_page_product"	NUMERIC NOT NULL,
	"product_name"	TEXT NOT NULL,
	"quantity"	TEXT NOT NULL,
	"quantity_units"	TEXT NOT NULL,
	"price"	TEXT NOT NULL,
	"price_units"	TEXT NOT NULL,
	"pvp"	TEXT NOT NULL,
	"ingredients"	TEXT NOT NULL,
	"bar_code"	TEXT NOT NULL,
	"is_new_arrival"	INTEGER NOT NULL,
	"previous_pvp"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "product_photos" (
	"id"	INTEGER NOT NULL,
	"photo_url"	TEXT NOT NULL,
	"product_id"	INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("product_id") REFERENCES "products"("id")
);

/*aqui faltarà posar una taula extra per a la informació nutricional*/