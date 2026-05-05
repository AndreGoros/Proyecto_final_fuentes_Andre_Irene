import re

def get_flex_regex(word):
    f = word.lower()
    f = f.replace("b", "B").replace("v", "B")
    f = f.replace("g", "G").replace("j", "G")
    f = f.replace("s", "S").replace("z", "S").replace("c", "S")
    f = f.replace("B", "[bv]").replace("G", "[gj]").replace("S", "[szc]")
    f = f.replace("rr", "r").replace("r", "r+")
    if not f.startswith("h"): f = "h?" + f
    return f

test_cases = [
    ("gitomate", "jitomate"),
    ("arros", "arroz"),
    ("cebolla", "sebolla"),
    ("uevo", "huevo"),
    ("baca", "vaca")
]

for query, target in test_cases:
    regex = get_flex_regex(query)
    match = re.search(regex, target, re.IGNORECASE)
    print(f"Query: '{query}' -> Regex: '{regex}'")
    print(f"  Target: '{target}' -> Match: {'YES' if match else 'NO'}")
