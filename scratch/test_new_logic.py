import re

PALABRAS_IGNORAR = {
    "piezas", "pz", "de", "con", "en", "el", "la", "los", "las", "un", "una", "y"
}

SINONIMOS_BUSQUEDA = {
    "litros": "lt",
    "litro":  "lt",
    "kilos":  "kg",
    "kilo":   "kg",
    "latas":  "lata",
    "paquetes": "paquete",
    "bolsas": "bolsa",
    "frascos": "frasco",
    "botes": "bote"
}

def parse_product_string(prod_str: str):
    prod_str = prod_str.strip().lower()
    cantidad = 1
    match = re.match(r"^(\d+)\s*[xX*]?\s*(.*)$", prod_str)
    if match:
        try:
            cantidad = int(match.group(1))
            prod_str = match.group(2)
        except ValueError:
            pass
    palabras = prod_str.split()
    filtradas = []
    for p in palabras:
        if p in PALABRAS_IGNORAR:
            continue
        p_norm = SINONIMOS_BUSQUEDA.get(p, p)
        filtradas.append(p_norm)
    busqueda = " ".join(filtradas) if filtradas else prod_str
    return cantidad, busqueda

def get_regex(termino_busqueda):
    palabras_query = [p for p in termino_busqueda.lower().split() if len(p) > 1]
    if not palabras_query:
        palabras_query = [termino_busqueda.lower()]
    palabras_flex = []
    for p in palabras_query:
        p_f = p.replace("rr", "r").replace("r", "r+")
        palabras_flex.append(p_f)
    
    distractores = ["harina", "bebida", "polvo", "galletas"]
    avoid_regex = "".join([f"(?!.*{d})" for d in distractores if d not in termino_busqueda.lower()])
    
    return avoid_regex + "".join([f"(?=.*{p})" for p in palabras_flex]) + ".*"

test_cases = [
    ("6 litros de leche lala", "leche pasteurizada caja lt entera lala"),
    ("2 latas de atun", "atun lata 130 gr en hojuelas en agua con aceite mazatun"),
    ("1 kg de papa", "papa kg granel alfablanca en malla sm"),
    ("arroz", "arroz bolsa 900 gr super extra verde valle")
]

for input_str, db_sample in test_cases:
    qty, term = parse_product_string(input_str)
    regex = get_regex(term)
    match = re.search(regex, db_sample, re.IGNORECASE)
    print(f"Input: '{input_str}' -> Term: '{term}'")
    print(f"  Regex: {regex}")
    print(f"  Result: {'MATCH' if match else 'FAIL'}")
    print("-" * 20)
