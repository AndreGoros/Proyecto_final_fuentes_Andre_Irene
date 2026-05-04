import os
from typing import List
from database import db

# ── Parámetros de búsqueda (sobreescribibles desde .env) ──────────────────
RADIO_METROS      = float(os.getenv("RADIO_KM", "10")) * 1000
PRECIO_GASOLINA   = float(os.getenv("PRECIO_GASOLINA_LT", "25.0"))   # MXN/litro
RENDIMIENTO_KM_LT = float(os.getenv("RENDIMIENTO_KM_LT", "12.0"))    # km/litro


async def optimizar_carrito(latitud: float, longitud: float, productos: List[str]):
    """
    1. Encuentra la sucursal más cercana de cada cadena (con su ubicación exacta).
    2. Para cada sucursal, busca cada producto filtrando TAMBIÉN por ubicación
       (misma cadena + misma sucursal identificada por cadena_raw).
    3. Calcula costo total = subtotal productos + costo gasolina ida y vuelta.
    """

    # ── Paso 1: Obtener las 15 sucursales FÍSICAS más cercanas ─────────────────
    # Agrupamos por coordenadas exactas, ya que "cadena_raw" no es único por sucursal física.
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
                "distancia_mts":{"$first": "$distancia"},
            }
        },
        {"$sort": {"distancia_mts": 1}},                     # Las más cercanas primero
        {"$limit": 15},                                      # Aumentamos a 15 para tener ~3 de cada cadena
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

        for prod in productos:
            # Regex: todas las palabras del producto deben aparecer
            palabras = [p for p in prod.lower().split() if len(p) > 1]
            regex_pattern = "".join([f"(?=.*{p})" for p in palabras]) + ".*"

            # ── Filtro INQUEBRANTABLE por coordenada física + producto ─────────
            item = await db.precios.find_one(
                {
                    "location.coordinates": suc["_id"],     # ← El ancla física real
                    "nombre_simplificado": {
                        "$regex": regex_pattern,
                        "$options": "i",
                    },
                },
                sort=[("precio", 1)],
            )

            if item:
                productos_encontrados.append({
                    "producto":     item["producto"],
                    "precio":       item["precio"],
                    "distancia_km": round(distancia_km, 2),
                })
                subtotal += item["precio"]
            else:
                productos_no_encontrados.append(prod)

        # Solo incluir sucursales donde se encontró al menos 1 producto
        if productos_encontrados:
            resultados_finales.append({
                "cadena":               suc["cadena"],
                "sucursal":             suc["sucursal"],
                "distancia_km":         round(distancia_km, 2),
                "productos_encontrados":productos_encontrados,
                "productos_no_encontrados": productos_no_encontrados,
                "subtotal_productos":   round(subtotal, 2),
                "costo_gasolina":       costo_gasolina,
                "total_viaje":          round(subtotal + costo_gasolina, 2),
            })

    # Ordenar de la opción más barata a la más cara (Costo Total)
    resultados_finales.sort(key=lambda x: x["total_viaje"])

    return resultados_finales
