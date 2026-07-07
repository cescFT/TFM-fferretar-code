select n.nom, n.unitat_mesura_nutrient, pn.quantitat
from producte_nutrients pn
inner join nutrients n on n.id = pn.nutrient_id
where producte_mercadona_id = '4706';


select * from product_photos where product_id = '86'