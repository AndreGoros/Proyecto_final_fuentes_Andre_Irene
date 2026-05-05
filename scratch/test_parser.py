import re

UNIDADES_IGNORAR = {
    "latas", "lata", "piezas", "pz", "kg", "kilos", "kilo", "litros", "litro", 
    "paquete", "pq", "cajas", "caja", "bolsa", "frasco", "botes", "bote"
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
    filtradas = [p for p in palabras if p not in UNIDADES_IGNORAR]
    
    busqueda = " ".join(filtradas) if filtradas else prod_str
    
    return cantidad, busqueda

test_cases = [
    "6 litros de leche lala",
    "3 chocorroles",
    "1 kg de papa",
    "4 latas de atun"
]

for tc in test_cases:
    qty, term = parse_product_string(tc)
    palabras = [p for p in term.lower().split() if len(p) > 1]
    regex_pattern = "".join([f"(?=.*{p})" for p in palabras]) + ".*"
    print(f"Input: '{tc}' -> Qty: {qty}, Term: '{term}', Palabras: {palabras}")
    print(f"  Regex: {regex_pattern}")
