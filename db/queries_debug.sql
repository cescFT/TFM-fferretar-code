select n.nom, n.unitat_mesura_nutrient, pn.quantitat
from producte_nutrients pn
inner join nutrients n on n.id = pn.nutrient_id
where producte_mercadona_id = '4706';


select * from product_photos where product_id = '86';

select p.id, p.id_product, p.category, p.subcategory, p.product_name, p.origin, p.ciqual_text_to_search
                from products p
                inner join product_photos ph on ph.product_id = p.id
                left join producte_nutrients pn on pn.producte_mercadona_id = p.id_product
                where
                    p.found_nutriments = 0 and
                    pn.nutrient_id is null
                group by p.id_product
                limit 15;

SELECT found_nutriments
                    from products p
                    where p.id_product = 21578
                        group by p.id_product;


select pn.producte_mercadona_id, n.id as id_nutrient, n.nom, pn.quantitat, n.unitat_mesura_nutrient
from producte_nutrients pn
inner join nutrients n on n.id = pn.nutrient_id
where
    pn.producte_mercadona_id in ("21578")