import os
from typing import List
from database import db

# ── Parámetros de búsqueda (sobreescribibles desde .env) ──────────────────
RADIO_METROS      = float(os.getenv("RADIO_KM", "10")) * 1000
PRECIO_GASOLINA   = float(os.getenv("PRECIO_GASOLINA_LT", "25.0"))   # MXN/litro
RENDIMIENTO_KM_LT = float(os.getenv("RENDIMIENTO_KM_LT", "12.0"))    # km/litro


import re

def parse_product_string(prod_str: str):
    """
    Intenta extraer la cantidad al inicio de la cadena.
    Ejemplos: 
    - "6 litros leche lala" -> (6, "litros leche lala")
    - "2latas atun dolores" -> (2, "latas atun dolores")
    - "12x huevo" -> (12, "huevo")
    """
    prod_str = prod_str.strip()
    # Regex más conservador: Número al inicio + opcionalmente 'x' o '*' + el resto
    # El resto se mantiene casi íntegro para no perder términos que existan en DB (como 'litros')
    match = re.match(r"^(\d+)\s*[xX*]?\s*(.*)$", prod_str)
    if match:
        try:
            cantidad = int(match.group(1))
            busqueda = match.group(2)
            if busqueda: # Evitar que "6" devuelva busqueda vacía
                return cantidad, busqueda
        except ValueError:
            pass
    return 1, prod_str

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
                "sucursal":     {"$first": "$cadena_raw"},
                "direccion":    {"$first": "$direccion"},
                "distancia_mts":{"$first": "$distancia"},
            }
        },
        {"$sort": {"distancia_mts": 1}},                     # Las más cercanas primero
        {"$limit": 15},
    ]

    sucursales = await db.precios.aggregate(pipeline_geo).to_list(length=15)

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
            palabras = [p for p in termino_busqueda.lower().split() if len(p) > 1]
            if not palabras:
                # Caso borde: si el string es muy corto, usarlo tal cual
                palabras = [termino_busqueda.lower()]
                
            regex_pattern = "".join([f"(?=.*{p})" for p in palabras]) + ".*"

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
