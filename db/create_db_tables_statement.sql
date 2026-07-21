DROP TABLE IF EXISTS "product_photos";
DROP TABLE IF EXISTS "products";
DROP TABLE IF EXISTS "nutrients";
DROP TABLE IF EXISTS "producte_nutrients";
DROP TABLE IF EXISTS "certifications";
DROP TABLE IF EXISTS "product_certifications";
DROP TABLE IF EXISTS "gemini_models";

CREATE TABLE "products" (
	"id"	INTEGER NOT NULL,
	"date_scraped"	TEXT NOT NULL,
	"week_num"	TEXT NOT NULL,
	"year"	TEXT NOT NULL,
	"postal_code"	TEXT NOT NULL,
    "ciqual_text_to_search"	TEXT NOT NULL,
	"found_nutriments"	INTEGER NOT NULL DEFAULT 0,
    "origin" TEXT NOT NULL,
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
	"nutriscore"	TEXT DEFAULT NULL,
    "planetscore" TEXT DEFAULT NULL,
    "ciqual_text" TEXT DEFAULT NULL,
    "ciqual_id" TEXT DEFAULT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "product_photos" (
	"id"	INTEGER NOT NULL,
	"photo_url"	TEXT NOT NULL,
	"product_id"	INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("product_id") REFERENCES "products"("id")
);

CREATE TABLE "nutrients" (
	"id"	INTEGER NOT NULL,
	"nom"	TEXT NOT NULL UNIQUE,
	"unitat_mesura_nutrient"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);

INSERT INTO nutrients (nom, unitat_mesura_nutrient) VALUES ('NO DATA', '-');
INSERT INTO nutrients (nom, unitat_mesura_nutrient) VALUES ('Energia (kcal)', 'kcal');
INSERT INTO nutrients (nom, unitat_mesura_nutrient) VALUES ('Energia (kJ)', 'kJ');

CREATE TABLE producte_nutrients (
	product_id INTEGER NOT NULL,
    producte_mercadona_id TEXT NOT NULL,
    nutrient_id INTEGER NOT NULL,
    quantitat REAL NOT NULL,
    PRIMARY KEY (product_id, nutrient_id),
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (nutrient_id) REFERENCES nutrients(id) ON DELETE RESTRICT
);


CREATE TABLE certifications (
	"id"	INTEGER NOT NULL,
	"certification_name"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);

INSERT INTO certifications (certification_name) VALUES ('No certificat');

CREATE TABLE "product_certifications" (
	"product_id"	INTEGER NOT NULL,
	"certification_id"	INTEGER,
	PRIMARY KEY("product_id", "certification_id"),
	FOREIGN KEY("product_id") REFERENCES "products"("id_product"),
    FOREIGN KEY("certification_id") REFERENCES "certifications"("id")
);

CREATE TABLE "gemini_models" (
	"id"	INTEGER NOT NULL,
	"model_name"	TEXT NOT NULL UNIQUE,
    "is_blocked" INTEGER NOT NULL DEFAULT 0,
    "last_petition" INTEGER NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);

INSERT INTO gemini_models (model_name, last_petition) VALUES ('gemini-2.5-flash', 1784638586);
INSERT INTO gemini_models (model_name) VALUES ('gemini-3.5-flash');
INSERT INTO gemini_models (model_name) VALUES ('gemini-3.1-flash-lite');