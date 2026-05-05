import re

def get_flex_regex(word):
    f = word.lower()
    if f.startswith("h"): f = "h?" + f[1:]
    else: f = "h?" + f
    f = f.replace("b", "[bv]").replace("v", "[bv]")
    f = f.replace("g", "[gj]").replace("j", "[gj]")
    f = f.replace("z", "[szc]").replace("s", "[szc]").replace("c", "[szc]")
    f = f.replace("rr", "r").replace("r", "r+")
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
