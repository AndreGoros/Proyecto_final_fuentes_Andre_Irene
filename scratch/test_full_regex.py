import re

def get_full_regex(termino_busqueda):
    palabras_query = [p for p in termino_busqueda.lower().split() if len(p) > 1]
    if not palabras_query:
        palabras_query = [termino_busqueda.lower()]
    
    palabras_flex = []
    for p in palabras_query:
        f = p.lower()
        f = f.replace("b", "B").replace("v", "B")
        f = f.replace("g", "G").replace("j", "G")
        f = f.replace("s", "S").replace("z", "S").replace("c", "S")
        f = f.replace("B", "[bv]").replace("G", "[gj]").replace("S", "[szc]")
        f = f.replace("rr", "r").replace("r", "r+")
        if not f.startswith("h"): f = "h?" + f
        palabras_flex.append(f)

    distractores = ["harina", "bebida", "polvo", "galletas"]
    avoid_regex = "".join([f"(?!.*{d})" for d in distractores if d not in termino_busqueda.lower()])
    
    return avoid_regex + "".join([f"(?=.*{p})" for p in palabras_flex]) + ".*"

test_cases = [
    ("leche lala", "leche pasteurizada lala"),
    ("jitomate", "jitomate"),
    ("cebolla", "cebolla"),
    ("arroz", "arroz bolsa")
]

for q, t in test_cases:
    regex = get_full_regex(q)
    match = re.search(regex, t, re.IGNORECASE)
    print(f"Query: '{q}' -> Regex: '{regex}'")
    print(f"  Target: '{t}' -> Match: {'YES' if match else 'NO'}")
