
import sys
import os

# Añadir el directorio backend al path para poder importar
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from services.query_service import parse_product_string

def test_parser():
    cases = [
        ("6 litros leche lala entera", (6, "litros leche lala entera")),
        ("2latas atun dolores", (2, "latas atun dolores")),
        ("1kg frijoles la costeña", (1, "kg frijoles la costeña")), # 1 no es extraído si no hay espacio o x? No, 1kg -> 1, kg...
        ("pan bimbo grande", (1, "pan bimbo grande")),
        ("3 x huevos san juan", (3, "huevos san juan")),
        ("12 piezas huevo", (12, "piezas huevo")),
        ("leche", (1, "leche")),
        ("6x yogurt", (6, "yogurt")),
    ]
    
    print("Testing parse_product_string (Updated):")
    print("-" * 30)
    for input_str, expected in cases:
        result = parse_product_string(input_str)
        status = "✅" if result == expected else "❌"
        print(f"{status} Input: '{input_str}'")
        print(f"   Expected: {expected}")
        print(f"   Got:      {result}")
    print("-" * 30)

if __name__ == "__main__":
    test_parser()
