"""
TFM: Food environment on grocery online supermarket

Author: Francesc Ferré Tarrés

This module rewrites the core of the EWO ingredient detection algorithm to correct two specific problems:

  BUG 1 — Deduplication by NAME instead of by POSITION
  --------------------------------------- --------------
  The original code would eventually remove a match if its name (e.g. ‘wheat’) was a substring of the name of another match already found (e.g. ‘wheat flour / white flour / ...’), REGARDLESS OF THE POSITION in the text where each was found. This causes false negatives: if the text contains ‘wholewheat’ in one place and ‘wheat flour’ in another (two real and independent occurrences), the entire ‘wheat’ was eventually deleted, even though it was a legitimate and unrelated find.

  The solution: instead of comparing names, we calculate the position (start, end) of EACH occurrence found in the text, and only discard a match when its text span is ACTUALLY overlapped by the span of a longer match (in the same area of the text). It's the classic ‘longest match wins’ / overlapping spans elimination algorithm (the same one spaCy uses with `filter_spans`).

  BUG 2 — Isolated words interpreted out of context
  ------------------------------------ ‘alto oleico vegetable oils (sunflower and olive)’ is interpreted
  as if it contains ‘sunflower’ and ‘olive’ as RAW ingredients (score 0
  in your Excel), when in reality it is sunflower oil / olive oil
  (score 4 / score 3). The phrase ‘aceite de girasol’ never appears literally and consecutively in the text, so the normal matcher cannot find it directly — but ‘girasol’ and “oliva” on their own do, and that is why the ‘Raw Sunflower’/‘Olive’ entries are triggered incorrectly.

  The solution (can only be resolved with domain knowledge, no purely textual technique solves it on its own): we detect the standard labelling pattern ‘<carrier> ... (from <origin1>, <origin2>...)’
  (mandatory by law for vegetable oils/fats: Regulation (EU)
  1169/2011, Annex VII), we reconstruct ‘<carrier> of <origin>’ and check
  if this compound phrase exists literally in your Excel. If it
  does, we generate a HIGHEST priority candidate exactly at the position
  of the origin word (‘sunflower’ inside the parenthesis). Since this candidate occupies the same span as the ‘raw’ match (‘Sunflower’ alone) would, the same overlap resolution from phase 2 (bug 1) already guarantees that the reconstructed match wins — the two corrections share a mechanism.

"""

import re
from grocery_scraper.utils.utils import normalize_text
from grocery_scraper.dto.ewo_reference import EwoReference, Candidate
import pandas as pd

NORMAL_FLOUR = [
    "harina de trigo", "harina blanca", "harina semiintegral",
    "harina integral", "harina semicompleta",
]

# Llista de patrons o cadenes complexes que no són ingredients objectiu
# i que causen falsos positius d'ingredients simples (ex: "agua" a "castaña de agua")
IGNORED_COMPOUND_PATTERNS = [
    r'\bcasta[ñn]as?\s+de\s+agua\b',
    r'\bbaño\s+de\s+agua\b',
    r'\bsuero\s+de\s+leche(?:\s+en\s+polvo)?\b',
    r'\barroz\s+inflado\b',
    r'\bcebollas?(?:\s+[\wáéíóúñ]+){0,3}?\s+encurtidas?\b',
    r'\bzanahorias?(?:\s+[\wáéíóúñ]+){0,3}?\s+encurtidas?\b',
    r'\bcebollas?(?:\s+[\wáéíóúñ]+){0,3}?\s+deshidratadas?\b',
    r'\bzumos?\s+de\s+lim[oó]n(?!\s+(?:concentrados?|a\s+partir\s+de\s+concentrados?))\b',
    r'\baceites?\s+de\s+s[eé]samo(?:\s+(?:de\s+(?:primera\s+)?presi[oó]n(?:\s+en\s+fr[ií]o)?|virgen|refinado|tostado))?\b',
    r'\bzumos?\s+de\s+mandarinas?\b',
    r'\bzumos?\s+de\s+naranjas?\b',
    r'\bajos?(?:\s+[\wáéíóúñ]+){0,3}?\s+deshidratados?\b',
    r'\bpastas?\s+de\s+tomates?(?:\s+(?:doble|triple|concentradas?|concentrados?))*\b',
    r'\bpastas?\s+de\s+avellanas?(?:\s+[\wáéíóúñ]+){0,2}?\b',
    r'\bpastas?\s+de\s+cacahuetes?(?:\s+[\wáéíóúñ]+){0,2}?\b',
    r'\bharinas?\s+de\s+arroz(?:\s+[\wáéíóúñ]+){0,2}?\b',
    r'\bextractos?\s+de\s+t[eé]s?(?:\s+[\wáéíóúñ]+){0,2}?\b',
    r'\bjarabes?\s+de\s+ma[ií]z(?:\s+[\wáéíóúñ]+){0,3}?\b',
    r'\bsalsas?\s+de\s+soja(?:\s+[\wáéíóúñ]+){0,3}?\b',
    r'\bzumos?\s+de\s+frutas?(?:\s+[\wáéíóúñ]+)*(?:\s*\([^)]*\))*',
    r'\bconcentrados?\s+de\s+frutas?\s+y\s+(?:verduras?|hortalizas?)(?:\s+[\wáéíóúñ]+)*(?:\s*\([^)]*\))*',
    r'\bcocos?\s+rallados?\b',
    r'\brellenos?\s+de\s+coco\b(?:\s*:?\s*\d+%\s*)?',
    r'\bcebollas?(?:\s+[\wáéíóúñ]+){0,2}?\s+caramelizadas?\b',
    r'\bextractos?\s+de\s+cocos?(?:\s+[\wáéíóúñ]+){0,2}?\b',
    r'\bl?eches?\s+de\s+cocos?(?:\s+[\wáéíóúñ]+){0,2}?\b',
    r'\baromas?\s+(?:natural(?:es)?\s+)?de\s+[\wáéíóúñ]+(?:[\s\-][\wáéíóúñ]+){0,2}?\b',
    r'\bcopos?\s+de\s+ma[ií]z(?:\s+[\wáéíóúñ]+){0,2}?\b',
    r'\bralladuras?\s+de\s+(?:naranjas?|lim[oó]nes?|limas?|c[ií]tricos?)(?:\s+[\wáéíóúñ]+){0,2}?\b',
    r'\bcalabac[ií]n(?:es)?(?:\s+[\wáéíóúñ]+){0,2}?\s+asados?\b',
    r'\bpastas?\s+de\s+cacahuetes?(?:\s+[\wáéíóúñ]+){0,2}?\b',
    r'\bharinas?\s+de\s+sojas?(?:\s+[\wáéíóúñ]+){0,3}?\b',
    r'\bprote[ií]nas?(?:\s+[\wáéíóúñ]+){0,2}?\s+de\s+sojas?(?:\s+[\wáéíóúñ]+){0,3}?\b',
    r'\bharinas?\s+de\s+avenas?(?:\s+[\wáéíóúñ]+){0,2}?\b',
    r'\bs[eé]molas?\s+de\s+arroz(?:\s+[\wáéíóúñ]+){0,2}?\b',
    r'\bsuero\s+de\s+leche(?:\s+en\s+polvo)?\b',
]

CARRIER_NOUNS = {
    "aceite": ["aceite", "aceites"],
    "grasa": ["grasa", "grasas"],
    "almidon": ["almidon", "almidones"],
    "harina": ["harina", "harinas"],
    "proteina": ["proteina", "proteinas"],
    "extracto": ["extracto", "extractos"],
    "fecula": ["fecula", "feculas"],
    "aroma": ["aroma", "aromas"],
    "semilla": ["semilla", "semillas"],
}

def build_name_lookup(ewo_ingredients: pd.DataFrame) -> dict:
    """
    Dictionary {normalised_name: (ingredient_names_complet, reference, score, row_id, sugar)}
    for EACH individual synonym (separated by ‘ / ’), used by phase 0
    (re-construction of source clauses) to check if "<carrier> of
    <source>" exists literally as an Excel entry.

    Args:
        ewo_ingredients (pd.DataFrame): DataFrame containing EWOnutri ingredients data.

    Returns:
        dict: Dictionary mapping normalised names to tuples of ingredient names, reference, score, row ID, and sugar content.
    """
    lookup = {}
    for row_id, row in ewo_ingredients.iterrows():
        if pd.isna(row['score']):
            continue
        ingredient_names = str(row['es']).strip() if pd.notna(row['es']) else ""
        reference = str(row['reference']).strip() if pd.notna(row['reference']) else ""
        sugar = row['sugar']
        if reference == 'nan':
            reference = ""
        score = int(row['score'])

        for synonym in ingredient_names.split(' / '):
            key = normalize_text(synonym.strip())
            if key and key not in lookup:
                lookup[key] = (ingredient_names, reference, score, row_id, sugar)
    return lookup


# ---------------------------------------------------------------------------
# PHASE 0 — Reconstruction of clauses ‘<portador> ... (from origin1, origin2)’
# ---------------------------------------------------------------------------

# ‘Carrier’ names that are often followed by an origin clause in
# parentheses: ‘vegetable oil (sunflower, palm)’, ‘vegetable fat (coconut)’...
# Extend this list as you find more cases in your corpus.

def _build_carrier_pattern() -> re.Pattern:
    """
    Function to make it better to refine ingredient list names.
    Args:
        None.
    Returns:
        re.Pattern: Regular expression pattern for carrier names.
    """

    all_forms = sorted(
        {f for forms in CARRIER_NOUNS.values() for f in forms},
        key=len, reverse=True
    )
    carrier_alt = '|'.join(re.escape(f) for f in all_forms)
    return re.compile(
        r'(?<!\w)(' + carrier_alt + r')\b'
        r'(?:\s+(?:vegetal(?:es)?|animal(?:es)?))*'
        r'[^,;()]*'
        r'\(\s*(?:de\s+)?([^)]+)\)'
    )

CARRIER_PATTERN = _build_carrier_pattern()


def _split_origin_list_with_offsets(raw: str, base_offset: int) -> list:
    """
    Split ‘sunflower, olive’ (or ‘sunflower and olive’) into tokens, returning
    for each one its (text, absolute_start, absolute_end) within the
    complete text. Calculate the EXACT position of each origin (and not just
    that of the whole clause) is what allows each to compete
    independently against its own ‘raw’ match (‘Sunflower’ alone,
    ‘Olive’ alone) in the resolution of overlaps -- without two
    sources from the same clause ‘stepping on’ each other.

    Args:
        raw(str): The input string to split.
        base_offset(int): The base offset for calculating absolute positions.

    Returns:
        list: List of tuples containing (text, absolute_start, absolute_end).
    """
    seps = list(re.finditer(r'\s*,\s*|\s+y\s+|\s+e\s+', raw))
    bounds, last = [], 0
    for sep in seps:
        bounds.append((last, sep.start()))
        last = sep.end()
    bounds.append((last, len(raw)))

    tokens = []
    for a, b in bounds:
        segment = raw[a:b]
        stripped = segment.strip()
        if not stripped:
            continue
        lead_ws = len(segment) - len(segment.lstrip())
        start = base_offset + a + lead_ws
        tokens.append((stripped, start, start + len(stripped)))
    return tokens

OIL_QUALIFIERS_PATTERN = r'\b(?:refinados?|virgen(?:es)?|extra|alto\s+oleico|desodorizados?|(?:parcialmente\s+)?hidrogenados?|prensados?\s+en\s+fr[ií]o)\b'
CARRIER_FALLBACKS = {
    "grasa": ["aceite"],
    "aceite": ["grasa"],
    "almidon": ["fecula"],
    "fecula": ["almidon"],
}

def reconstruct_carrier_matches(text: str, name_lookup: dict) -> list:
    """
    For each ‘<carrier> ... (of X, Y)’ found, check if "<carrier>
    of <origin>" exists in the knowledge base. If it does, a candidate is generated
    with the EXACT position of the origin word (e.g.
    only ‘sunflower’ within ‘(from sunflower and olive)’).

    Since this candidate has priority 0 (the highest) and occupies the same
    text segment as the “raw” phase 1 match (“Girasol” on its own),
    the overlap resolution (phase 2) already guarantees that the
    reconstructed match will win -- there is no need to “erase” the text.

    Args:
        text(str): The input text to process.
        name_lookup(dict): The name lookup dictionary.

    Returns:
        list: List of Candidate objects.
    """
    candidates: list[Candidate] = []

    for m in CARRIER_PATTERN.finditer(text):
        carrier_raw = m.group(1)
        carrier_singular = next(
            base for base, forms in CARRIER_NOUNS.items() if carrier_raw in forms
        )
        origin_tokens = _split_origin_list_with_offsets(m.group(2), m.start(2))

        # Portadors a provar: el portador trobat + els seus equivalents (ex: ["grasa", "aceite"])
        carriers_to_try = [carrier_singular] + CARRIER_FALLBACKS.get(carrier_singular, [])

        for origin, o_start, o_end in origin_tokens:
            hit = None

            # Busquem provant tots els portadors equivalents
            for carrier in carriers_to_try:
                # 1. Cerca directa (ex: "grasa de girasol refinado" / "aceite de girasol refinado")
                compound_key = normalize_text(f"{carrier} de {origin}")
                hit = name_lookup.get(compound_key)
                if hit:
                    break

                # 2. Cerca netejant adjectius (ex: "grasa de girasol" / "aceite de girasol")
                clean_origin = re.sub(OIL_QUALIFIERS_PATTERN, '', origin, flags=re.IGNORECASE).strip()
                clean_origin = re.sub(r'\s+', ' ', clean_origin)
                compound_key_clean = normalize_text(f"{carrier} de {clean_origin}")
                hit = name_lookup.get(compound_key_clean)
                if hit:
                    break

            if hit:
                ref_name, reference, score, row_id, sugar = hit
                candidates.append(Candidate(
                    start=o_start, end=o_end, priority=0,
                    ewo_ref=EwoReference(ref_name, reference, score, sugar,
                                         row_id=row_id, span=(o_start, o_end))
                ))

    return candidates


# ---------------------------------------------------------------------------
# PHASE 1 — Generation of candidates (all occurrences, with their
# exact position), preserving the 4 special rules of your original code
# (vitamins, concentrated juice, gluten, non-standard flours).
# ---------------------------------------------------------------------------

def mask_barley_malt_origins(text: str) -> str:
    """
    Mask “barley” when it follows “malt syrup/extract”,
    leaving “malt syrup” intact to thrash with Excel and preventing “barley” from popping up as a separate raw cereal.

    Args:
        text (str): The input text to mask.

    Returns:
        str: The masked text.
    """
    pattern = r'(\b(?:jarabes?|extractos?)\s+de\s+malta\s+)de\s+cebadas?\b'

    def _replace_barley(m: re.Match) -> str:
        prefix = m.group(1)  # Manté "jarabe de malta "
        full_match = m.group(0)
        # Substitueix 'de cebada' per espais en blanc
        spaces = ' ' * (len(full_match) - len(prefix))
        return prefix + spaces

    return re.sub(pattern, _replace_barley, text, flags=re.IGNORECASE)



def mask_vinegar_origins(text: str) -> str:
    """
    Mask “rice” when it follows “vinegar”, keeping the word “vinegar” intact and avoiding a false positive for rice.

    Args:
        text (str): Text to be processed.

    Returns:
        str: Text with masked occurrences.
    """
    pattern = r'(\bvinagres?\s+)(de\s+arroz\b)'

    def _replace_rice(m: re.Match) -> str:
        return m.group(1) + ' ' * len(m.group(2))

    return re.sub(pattern, _replace_rice, text, flags=re.IGNORECASE)

def mask_additive_origins(text: str) -> str:
    """
    Spaced-mask the parenthetical source of the additive (e.g. “(soy)”, “(from soy)”)
    when it follows an E322 / E-322 code or an emulsifier, leaving the E code intact.

    Args:
        text (str): Text to be processed.

    Returns:
        str: Text with additive origins masked.
    """
    # Patró que captura (1: codi E) i (2: origen entre parèntesis)
    pattern = r'(\be\s*[-_]?\s*\d+[a-z]?\b\s*)(\(\s*(?:de\s+)?(?:soja|girasol|palma|colza)\s*\))'

    def _replace_origin(m: re.Match) -> str:
        """
        Replaces the additive origin with spaces of the same length.
        Args:
            m (re.Match): Matches to be ignored.

        Returns:
            str: Ignored compound pattern replaced with spaces.
        """
        return m.group(1) + ' ' * len(m.group(2))


    return re.sub(
        pattern,
        _replace_origin,
        text,
        flags=re.IGNORECASE
    )

def mask_unwanted_seeds_in_mixes(text: str) -> str:
    """
    Replace the words "girasol" and "calabaza" with spaces ONLY when they appear
    inside a parenthesis of "mezcla de semillas (...)".
    """

    def _clean_mix_content(match: re.Match) -> str:
        mix_text = match.group(0)
        # 'girasol' té 7 lletres -> 7 espais
        mix_text = re.sub(r'\bgirasol\b', '       ', mix_text, flags=re.IGNORECASE)
        # 'calabaza' té 8 lletres -> 8 espais
        mix_text = re.sub(r'\bcalabaza\b', '        ', mix_text, flags=re.IGNORECASE)
        return mix_text

    # Patró que localitza "mezcla de semillas" seguit de la seva llista entre parèntesis
    pattern = r'\bmezcla\s+de\s+semillas?\s*\([^)]*\)'

    return re.sub(pattern, _clean_mix_content, text, flags=re.IGNORECASE)

def mask_ignored_phrases(text: str) -> str:
    """
    Replaces unwanted phrases with spaces of the same length.
    This removes noise without altering the position indices (spans) of the rest of the text.
    Args:
        text (str): Text to be processed.

    Returns:
        str: Text with unwanted phrases replaced with spaces.
    """
    text = mask_barley_malt_origins(text)  # "jarabe de malta de cebada" -> "jarabe de malta          "
    text = mask_vinegar_origins(text)  # "vinagre de arroz" -> "vinagre         "

    # 2. Altres opcions i llavors
    text = mask_unwanted_seeds_in_mixes(text)
    text = mask_additive_origins(text)

    def _replace_with_spaces(match: re.Match) -> str:
        """
        Auxiliary function to replace with spaces ignored coumpound patterns.
        Args:
            match (re.Match): Matches to be ignored.

        Returns:
            str: Ignored compound pattern replaced with spaces.
        """
        return ' ' * len(match.group(0))

    for pattern in IGNORED_COMPOUND_PATTERNS:
        text = re.sub(
            pattern,
            _replace_with_spaces,
            text,
            flags=re.IGNORECASE
        )
    return text

def generate_candidates(
    text: str,
    ewo_ingredients: pd.DataFrame,
    product_certifications: list
) -> tuple:
    """
    `normal_candidates` are positional occurrences, subject to the
    phase 2 overlap resolution (Exxx references and names).

    `derived_matches` are the 2 rules that do not correspond to any segment
    literal of the name itself (‘vitaminas_anadidas_no_e’,
    ‘zumo_concentrado_no_limon’): are calculated facts, not text occurrences,
    so they are added directly without competing for space with
    any other match.

    Args:
        text: The text to be processed.
        ewo_ingredients: DataFrame containing EWO ingredients.
        product_certifications: List of product certifications.

    Returns:
        tuple: A tuple containing normal_candidates and derived_matches.
    """

    candidates: list[Candidate] = []
    derived: list[EwoReference] = []

    gluten_free_cert = any(
        c.get_certification_name() == 'gluten-free' for c in product_certifications
    )
    has_sin_gluten = re.search(r'(?<!\w)sin gluten(?!\w)', text) is not None

    has_concentrated_lemon_juice = False  # es calcula dins del bucle

    for row_id, row in ewo_ingredients.iterrows():
        score = row['score']
        if pd.isna(score):
            continue

        ingredient_names = str(row['es']).strip() if pd.notna(row['es']) else ""
        ingredient_names_splitted = ingredient_names.split(' / ')
        reference_ingredient = str(row['reference']).strip() if pd.notna(row['reference']) else ""
        sugar = row['sugar']
        score = int(score)
        if reference_ingredient == 'nan':
            reference_ingredient = ""

        # --- referencia Exxx: te prioritat i, si es troba, no cal mirar noms ---
        if reference_ingredient:
            ref_norm = normalize_text(reference_ingredient)

            # Normalitzem la referència per extreure la part numèrica si comença per 'e' (ex: e339, e-339, e 339)
            # Permet trobar formats com "e 339", "e-339" o "e339"
            match_e = re.match(r'^e\s*[-_]?\s*(\d+[a-z]?)$', ref_norm)

            if match_e:
                number_part = match_e.group(1)
                # Patró regex que accepta: "e339", "e-339", "e 339", etc.
                pattern = r'(?<!\w)e\s*[-_]?\s*' + re.escape(number_part) + r'(?!\w)'
                matches = list(re.finditer(pattern, text))
            else:
                # Comportament per defecte si no compleix el patró 'E...'
                pattern = r'(?<!\w)' + re.escape(ref_norm) + r'(?!\w)'
                matches = list(re.finditer(pattern, text))
                if not matches:
                    ref_no_dash = ref_norm.replace('-', '')
                    pattern = r'(?<!\w)' + re.escape(ref_no_dash) + r'(?!\w)'
                    matches = list(re.finditer(pattern, text))

            if matches:
                for mo in matches:
                    candidates.append(Candidate(
                        start=mo.start(), end=mo.end(), priority=1,
                        ewo_ref=EwoReference(ingredient_names, reference_ingredient, score, sugar,
                                             row_id=row_id, span=(mo.start(), mo.end()))
                    ))
                continue

        # --- noms (amb els 4 casos especials del vostre codi original) ---
        for ingredient_name in ingredient_names_splitted:
            name_norm = normalize_text(ingredient_name.strip())

            if name_norm == "vitaminas_anadidas_no_e":
                pattern = r'(?:^|[,;(])\s*vitaminas?\b'
                not_have_vit_e = True
                for vm in re.finditer(pattern, text):
                    text_after = text[vm.end():vm.end() + 100]
                    vitamins = re.findall(
                        r'\b(?:a\d{0,2}|b\d{0,2}|c|d\d{0,2}|e|f|k\d{0,2})\b', text_after
                    )
                    if vitamins and 'e' in vitamins:
                        not_have_vit_e = False
                        break
                if re.search(pattern, text) and not_have_vit_e:
                    derived.append(EwoReference(ingredient_names, reference_ingredient, score,sugar, row_id=row_id))
                continue

            if name_norm == "zumo_concentrado_no_limon":
                pattern = r'\bzumo\s+concentrado\s+de\s+([^;().]+)'
                if not re.search(pattern, text):
                    continue
                juices = []
                for jm in re.finditer(pattern, text):
                    for fruit in re.split(r'\s*,\s*|\s+y\s+', jm.group(1).strip()):
                        fruit = fruit.strip()
                        if fruit:
                            juices.append(fruit)
                if any(j == 'limon' for j in juices):
                    if not has_concentrated_lemon_juice:
                        derived.append(EwoReference("zumo concentrado de limon", "", 0, False, row_id=row_id))
                        has_concentrated_lemon_juice = True
                else:
                    derived.append(EwoReference(ingredient_names, reference_ingredient, score, True, row_id=row_id))
                continue

            if name_norm == "gluten":
                if gluten_free_cert or has_sin_gluten:
                    continue
                pattern = r'(?<!\w)gluten(?!\w)'
                for mo in re.finditer(pattern, text):
                    candidates.append(Candidate(
                        start=mo.start(), end=mo.end(), priority=2,
                        ewo_ref=EwoReference(ingredient_names, reference_ingredient, score, sugar,
                                             row_id=row_id, span=(mo.start(), mo.end()))
                    ))
                continue

            if name_norm == "no_harinas_normales":
                if not re.search(r'\bharinas?\b', text):
                    continue
                if any(re.search(r'(?<!\w)' + re.escape(f) + r'(?!\w)', text) for f in NORMAL_FLOUR):
                    continue
                derived.append(EwoReference(ingredient_names, reference_ingredient, score, sugar, row_id=row_id))
                continue

            # --- cas general: nom normal, es guarda CADA ocurrencia amb la seva posicio ---
            pattern = r'(?<!\w)' + re.escape(name_norm) + r'(?!\w)'
            for mo in re.finditer(pattern, text):
                candidates.append(Candidate(
                    start=mo.start(), end=mo.end(), priority=2,
                    ewo_ref=EwoReference(ingredient_names, reference_ingredient, score, sugar,
                                         row_id=row_id, span=(mo.start(), mo.end()))
                ))

    return candidates, derived


# ---------------------------------------------------------------------------
# PHASE 2 — Resolving overlaps by POSITION (replaces bug 1)
# ---------------------------------------------------------------------------

def resolve_overlaps(candidates: list) -> list:
    """
    "The longest match wins": order by priority and then by descending length,
    and accept a candidate only if its span does not overlap with any
    already accepted span.

    Args:
        candidates: List of Candidate objects.

    Returns:
        list: A list of Candidate objects with overlaps resolved.
    """

    ordered = sorted(candidates, key=lambda c: (c.priority, -c.length, c.start))
    accepted: list[Candidate] = []

    def overlaps(a: Candidate, b: Candidate) -> bool:
        return a.start < b.end and b.start < a.end

    for cand in ordered:
        if not any(overlaps(cand, acc) for acc in accepted):
            accepted.append(cand)

    return accepted


def match_ewo_ingredients(
    ingredients_text: str,
    ewo_ingredients: pd.DataFrame,
    product_certifications: list
) -> list:
    """
    Function created by Claude AI with the aim to improve algorithm created by myself.
    It improves things such as ingredients like "harina de trigo" and "trigo" when "trigo" is contained in
    "harina de trigo" and it must be ignored and ingredients with parenthesis like "aceites vegetales (de girasol y oliva)"..
    Args:
        ingredients_text (str): Text to match ingredients.
        ewo_ingredients (pd.DataFrame): DataFrame with ingredients to match.
        product_certifications (list): List of product certifications.

    Returns:
        list: List of accepted ingredients.
    """
    ingredients_text = ingredients_text.replace('[', '(').replace(']', ')')
    ingredients_text = ingredients_text.replace('{', '(').replace('}', ')')
    ingredients_text = mask_ignored_phrases(ingredients_text)
    name_lookup = build_name_lookup(ewo_ingredients)

    phase0_candidates = reconstruct_carrier_matches(ingredients_text, name_lookup)
    phase1_candidates, derived = generate_candidates(ingredients_text, ewo_ingredients, product_certifications)

    all_candidates = phase0_candidates + phase1_candidates
    accepted = resolve_overlaps(all_candidates)

    # una entrada per fila de l'Excel (row_id), encara que tingui diverses
    # ocurrencies acceptades al text
    seen_rows = set()
    results: list[EwoReference] = []
    for cand in sorted(accepted, key=lambda c: c.start):
        rid = cand.ewo_ref.row_id
        if rid not in seen_rows:
            seen_rows.add(rid)
            results.append(cand.ewo_ref)

    results.extend(derived)
    return results
