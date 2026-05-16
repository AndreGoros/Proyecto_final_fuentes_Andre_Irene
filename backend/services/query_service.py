import os
from typing import List
from database import db

# ── Parámetros de búsqueda (sobreescribibles desde .env) ──────────────────
RADIO_METROS      = float(os.getenv("RADIO_KM", "10")) * 1000
PRECIO_GASOLINA   = float(os.getenv("PRECIO_GASOLINA_LT", "25.0"))   # MXN/litro
RENDIMIENTO_KM_LT = float(os.getenv("RENDIMIENTO_KM_LT", "12.0"))    # km/litro


import re
from dotenv import load_dotenv

load_dotenv()
import unicodedata

def remove_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")

# Palabras que suelen venir en la consulta del usuario pero que estorban en la búsqueda en DB
PALABRAS_IGNORAR = {
    "piezas", "pz", "de", "con", "en", "el", "la", "los", "las", "un", "una", "y"
}

# Normalización de términos para que coincidan con la DB (ej. 'litros' -> 'lt')
SINONIMOS_BUSQUEDA = {
    "litros": "lt",
    "litro":  "lt",
    "kilos":  "kg",
    "kilo":   "kg",
    "gr":     "g",
    "gramos": "g",
    "leches": "leche",
    "huevos": "huevo",
    "latas":  "lata",
    "paquetes": "paquete",
    "bolsas": "bolsa",
    "frascos": "frasco",
    "botes": "bote",
    "jitomates": "jitomate",
    "cebollas": "cebolla",
    "un": "1",
    "una": "1",
    "uno": "1"
}

def parse_product_string(prod_str: str):
    """
    Extrae cantidad y normaliza unidades (ej: 500gr -> 0.5kg).
    """
    prod_str = remove_accents(prod_str.strip().lower())
    
    # 1. Detectar cantidad y posible unidad pegada (ej: 500gr, 2lt)
    cantidad = 1.0
    match = re.match(r"^(\d+(?:\.\d+)?)\s*([a-zA-Z]*)\s*[xX*]?\s*(.*)$", prod_str)
    
    if match:
        num_str = match.group(1)
        unit_str = match.group(2).lower()
        rest_str = match.group(3)
        
        try:
            cantidad = float(num_str)
            # Si la unidad es gramos, convertimos a fracción de kilo (el precio suele ser por kg)
            if unit_str in ["gr", "g", "gramos"]:
                cantidad = cantidad / 1000.0
                prod_str = rest_str
            elif unit_str in ["oz", "onza", "onzas"]:
                cantidad = cantidad * 0.02835
                prod_str = rest_str
            elif unit_str in ["lb", "libra", "libras"]:
                cantidad = cantidad * 0.4536
                prod_str = rest_str
            elif unit_str in ["kg", "kilos", "kilo"]:
                prod_str = rest_str
            elif unit_str in ["lt", "litro", "litros", "l"]:
                prod_str = rest_str
            else:
                # Si no es una unidad de peso/volumen, podría ser una unidad de conteo (ej: 2 latas)
                # O simplemente el nombre del producto empezaba con letras
                if unit_str:
                    prod_str = unit_str + " " + rest_str
                else:
                    prod_str = rest_str
        except ValueError:
            pass
            
    # 2. Limpiar palabras irrelevantes y normalizar sinónimos
    palabras = prod_str.split()
    filtradas = []
    for p in palabras:
        if p in PALABRAS_IGNORAR:
            continue
        p_norm = SINONIMOS_BUSQUEDA.get(p, p)
        # Manejo de "un", "una" como cantidad 1
        if p_norm in ["un", "una", "uno"]:
            continue
        filtradas.append(p_norm)
    
    busqueda = " ".join(filtradas) if filtradas else prod_str
    
    return cantidad, busqueda

async def optimizar_carrito(latitud: float, longitud: float, productos: List[str]):
    print(f"DEBUG: optimizar_carrito lat={latitud}, lon={longitud}, radio={RADIO_METROS}")
    """
    1. Encuentra la sucursal más cercana de cada cadena.
    2. Procesa cada string para extraer cantidad y término de búsqueda.
    3. Para cada sucursal, busca cada producto filtrando por ubicación.
    4. Calcula costo total multiplicando por cantidad + gasolina.
    """

    # ── Paso 1: Obtener las 15 sucursales FÍSICAS más cercanas ─────────────────
    pipeline_geo = [
        {
            "$geoNear": {
                "near": {"type": "Point", "coordinates": [longitud, latitud]},
                "distanceField": "distancia",
                "maxDistance": RADIO_METROS,
                "spherical": True,
            }
        },
        {
            "$group": {
                "_id": "$location.coordinates",              # Coordenada exacta = Sucursal única
                "cadena":       {"$first": "$cadena"},
                "sucursal":     {"$first": "$cadena"},       # Usamos el nombre normalizado
                "direccion":    {"$first": "$direccion"},
                "distancia_mts":{"$first": "$distancia"},
            }
        },
        {"$sort": {"distancia_mts": 1}},                     # Las más cercanas primero
        {"$limit": 15},
    ]

    sucursales = await db.precios.aggregate(pipeline_geo).to_list(length=15)
    print(f"DEBUG: Sucursales encontradas en el radio: {len(sucursales)}")

    resultados_finales = []

    for suc in sucursales:
        distancia_km    = suc["distancia_mts"] / 1000.0
        litros          = (distancia_km * 2) / RENDIMIENTO_KM_LT
        costo_gasolina  = round(litros * PRECIO_GASOLINA, 2)

        productos_encontrados = []
        productos_no_encontrados = []
        subtotal = 0.0

        for prod_original in productos:
            cantidad, termino_busqueda = parse_product_string(prod_original)
            
            # Regex: todas las palabras del término de búsqueda deben aparecer
            palabras_query = [p for p in termino_busqueda.lower().split() if len(p) > 1]
            if not palabras_query:
                # Caso borde: si el string es muy corto, usarlo tal cual
                palabras_query = [termino_busqueda.lower()]
                
            # Flexibilidad fonética para errores comunes en español (g/j, s/z/c, b/v, h muda)
            palabras_flex = []
            for p in palabras_query:
                f = p.lower()
                
                # Manejo de plurales: si termina en 's', hacerla opcional
                if f.endswith("s") and len(f) > 3:
                    f = f[:-1] + "s?"
                
                # Reemplazos con placeholders para evitar anidamiento
                f = f.replace("b", "B").replace("v", "B")
                f = f.replace("g", "G").replace("j", "G")
                f = f.replace("s", "S").replace("z", "S").replace("c", "S")
                
                # Reemplazo final de placeholders
                f = f.replace("B", "[bv]").replace("G", "[gj]").replace("S", "[szc]")
                
                # r/rr
                f = f.replace("rr", "r").replace("r", "r+")
                
                # Hack para palabras juntas (ej: piñamiel -> piña.*miel)
                # Si la palabra es larga y contiene "miel", "pavo", "lala", etc., insertar .*
                for together in ["miel", "pavo", "lala", "blanco", "negro"]:
                    if together in f and f != together:
                        f = f.replace(together, f".*{together}")

                # h opcional solo si no empieza con un grupo o clase
                if not f.startswith("["):
                    f = "h?" + f
                
                palabras_flex.append(f)

            # Evitar distractores comunes si no fueron pedidos explícitamente (ej. evitar 'harina de arroz' si pidió 'arroz')
            distractores = ["harina", "bebida", "polvo", "galletas"]
            avoid_regex = "".join([f"(?!.*{d})" for d in distractores if d not in termino_busqueda.lower()])
            
            regex_pattern = avoid_regex + "".join([f"(?=.*{p})" for p in palabras_flex]) + ".*"
            print(f"  DEBUG: Buscando '{prod_original}' -> Term: '{termino_busqueda}' -> Regex: '{regex_pattern}'")

            # ── Filtro por coordenada física + producto ─────────
            item = await db.precios.find_one(
                {
                    "location.coordinates": suc["_id"],
                    "nombre_simplificado": {
                        "$regex": regex_pattern,
                        "$options": "i",
                    },
                },
                sort=[("precio", 1)],
            )
            
            if item:
                print(f"    DEBUG: [OK] Encontrado en {suc['cadena']}: {item['producto']} (${item['precio']})")
            else:
                print(f"    DEBUG: [X] NO ENCONTRADO en {suc['cadena']}")

            if item:
                precio_unitario = item["precio"]
                precio_total = round(precio_unitario * cantidad, 2)
                
                productos_encontrados.append({
                    "producto":        item["producto"],
                    "precio_unitario": precio_unitario,
                    "cantidad":        cantidad,
                    "precio_total":    precio_total,
                    "distancia_km":    round(distancia_km, 2),
                })
                subtotal += precio_total
            else:
                productos_no_encontrados.append(prod_original)

        if productos_encontrados:
            dir_str = suc.get("direccion")
            if not dir_str or str(dir_str).lower() == "nan":
                dir_str = "Dirección no disponible"

            resultados_finales.append({
                "cadena":               suc["cadena"],
                "sucursal":             suc["sucursal"],
                "direccion":            dir_str,
                "distancia_km":         round(distancia_km, 2),
                "productos_encontrados":productos_encontrados,
                "productos_no_encontrados": productos_no_encontrados,
                "subtotal_productos":   round(subtotal, 2),
                "costo_gasolina":       costo_gasolina,
                "total_viaje":          round(subtotal + costo_gasolina, 2),
            })

    resultados_finales.sort(key=lambda x: x["total_viaje"])
    return resultados_finales
