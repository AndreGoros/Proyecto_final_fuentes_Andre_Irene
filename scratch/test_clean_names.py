import re

def clean_name(name):
    return name.replace("atén", "atún").replace("tehuacµn", "tehuacán")

test_names = [
    "atén en agua",
    "huevo blanco tehuacµn",
    "atén ahumado"
]

for n in test_names:
    print(f"Original: {n} -> Cleaned: {clean_name(n)}")
