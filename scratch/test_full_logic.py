import unicodedata
import re

def remove_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")

def parse_product_string(prod_str: str):
    prod_str = remove_accents(prod_str.strip().lower())
    # ... logic simplified ...
    return prod_str

def get_regex(termino_busqueda):
    palabras_query = termino_busqueda.split()
    palabras_flex = []
    for p in palabras_query:
        f = p.lower()
        f = f.replace("b", "B").replace("v", "B")
        f = f.replace("g", "G").replace("j", "G")
        f = f.replace("s", "S").replace("z", "S").replace("c", "S")
        f = f.replace("B", "[bv]").replace("G", "[gj]").replace("S", "[szc]")
        f = f.replace("rr", "r").replace("r", "r+")
        if not f.startswith("["): f = "h?" + f
        palabras_flex.append(f)
    
    distractores = ["harina", "bebida", "polvo", "galletas"]
    avoid_regex = "".join([f"(?!.*{d})" for d in distractores if d not in termino_busqueda])
    return avoid_regex + "".join([f"(?=.*{p})" for p in palabras_flex]) + ".*"

# Test 'atún'
input_val = "2 latas de atún"
term = parse_product_string(input_val)
regex = get_regex(term)
db_val = "atun lata 140 gr"
match = re.search(regex, db_val, re.IGNORECASE)

print(f"Term: {term}")
print(f"Regex: {regex}")
print(f"Match: {'YES' if match else 'NO'}")
