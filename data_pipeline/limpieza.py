"""
data_pipeline/limpieza.py
=========================
Limpieza, normalización y carga a MongoDB de datos de precios por cadena.
 
Transformaciones aplicadas:
  1. Filtrado por cadenas permitidas (Walmart, Soriana, Chedraui, La Comer)
  2. Limpieza y validación de precios (nulos, negativos, outliers por IQR)
  3. Normalización de nombres de cadena
  4. Creación de `nombre_simplificado` para matching con Gemini
  5. Construcción del objeto GeoJSON `location` requerido por MongoDB $geoNear
  6. Descarte de columnas de ruido
  7. Inserción por lotes en MongoDB (insert_many)
"""
 
from __future__ import annotations
 
import argparse
import logging
import os
import re
import sys
from pathlib import Path
from typing import Any
 
import pandas as pd
from pymongo import MongoClient, GEOSPHERE, UpdateOne
from pymongo.collection import Collection
from dotenv import load_dotenv

# Cargar variables de entorno desde .env (incluye MONGO_URI de Atlas)
load_dotenv()
 
# ---------------------------------------------------------------------------
# Configuración global
# ---------------------------------------------------------------------------
 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)
 
# Cadenas comerciales aceptadas → forma canónica
CADENAS_PERMITIDAS: dict[str, str] = {
    # Walmart y variantes
    "walmart":                  "Walmart",
    "wal-mart":                 "Walmart",
    "walmart supercenter":      "Walmart",
    "walmart express":          "Walmart",
    "wal-mart express":         "Walmart",   # variante real en CSV
    "walmart to go":            "Walmart",
    "bodega aurrera":           "Walmart",   # filial de Walmart México
    "bodega aurrera express":   "Walmart",   # variante real en CSV
    "mi bodega aurrera":        "Walmart",
    "superama":                 "Walmart",
    # Soriana y variantes
    "soriana":                  "Soriana",
    "soriana mercado":          "Soriana",
    "soriana hiper":            "Soriana",
    "soriana super":            "Soriana",
    "soriana express":          "Soriana",
    "hipermercado soriana":     "Soriana",   # variante real en CSV
    "mega soriana":             "Soriana",   # variante real en CSV
    "mercado soriana":          "Soriana",   # variante real en CSV
    # Chedraui y variantes
    "chedraui":                 "Chedraui",
    "chedraui selecto":         "Chedraui",
    "super chedraui":           "Chedraui",  # variante real en CSV
    # La Comer y variantes
    "la comer":                 "La Comer",
    "lacomer":                  "La Comer",
    "city market":              "La Comer",
    "fresko":                   "La Comer",
    "fresko la comer":          "La Comer",  # variante real en CSV
    "sumesa":                   "La Comer",
}
 
# Columnas que se descartan (ruido) — nombres reales del CSV
COLUMNAS_DESCARTADAS: list[str] = [
    # columnas de ubicación textual (ya tenemos lat/lon, pero el usuario pidió conservar direccion)
    "giro", "municipio", "estado", "nombre_comercial",
    # columnas de catálogo (muy específicas, no útiles para Gemini)
    "catalogo",
    # columnas legacy / alternativas
    "NombreComercial", "RazonSocial", "Estatus", "Tipo",
    "Giro", "Municipio", "Estado",          # mayúsculas por si vienen así
]
 
# Mapa de renombrado: columna real del CSV → nombre interno del pipeline
# Soporta tanto el formato original (mayúsculas) como el real (minúsculas)
COLUMNAS_MAP: dict[str, str] = {
    # Formato real del CSV (minúsculas)
    "cadena_comercial": "Cadena",
    "producto":         "Producto",
    "precio":           "Precio",
    "latitud":          "LATITUD",
    "longitud":         "LONGITUD",
    "direccion":        "direccion",
    # Formato original previsto (mayúsculas) — por compatibilidad
    "Cadena":           "Cadena",
    "Producto":         "Producto",
    "Precio":           "Precio",
    "LATITUD":          "LATITUD",
    "LONGITUD":         "LONGITUD",
    "Direccion":        "direccion",
}
 
# Columnas que DEBEN existir en el CSV (mínimo), en forma interna
COLUMNAS_REQUERIDAS: set[str] = {
    "Cadena", "Producto", "Precio", "LATITUD", "LONGITUD",
}
 
# Límites outlier (IQR × k) - Aumentado para proteger carne y productos caros
IQR_K = 10.0
 
# Configuración MongoDB por defecto (sobreescribible vía argumentos CLI)
MONGO_URI_DEFAULT    = os.getenv("MONGO_URI", "mongodb://pipeline_user:pipeline1234@localhost:27017/precios_db?authSource=admin")
MONGO_DB_DEFAULT     = os.getenv("MONGO_DB", os.getenv("MONGO_DB_NAME", "precios_db"))
MONGO_COL_DEFAULT    = os.getenv("MONGO_COLLECTION", "precios")
BATCH_SIZE           = 1_000          # documentos por insert_many
 
# ---------------------------------------------------------------------------
# Helpers de normalización
# ---------------------------------------------------------------------------
 
_RE_ESPACIOS = re.compile(r"\s+")
_RE_EXTRA    = re.compile(r"[^\w\s]")
 
 
# Mapeo de corrupciones de caracteres comunes en CSV de PROFECO
MAPA_CORRECCION = {
    "atén": "atún",
    "maöz": "maíz",
    "azécar": "azúcar",
    "hémeda": "húmeda",
    "cµpsulas": "cápsulas",
    "tama¥o": "tamaño",
    "jos©": "jose",
    "m xico": "mexico",
    "jamàn": "jamón",
    "clµsico": "clásico",
    "pi¥a": "piña",
    "piïa": "piña",
    "tiburàn": "tiburón",
    "piquön": "piquín",
    "fàrmula": "fórmula",
    "àn": "ón",
    "ö": "í",
    "µ": "a",
    "¥": "ñ",
    "à": "ó",
}

import unicodedata

def remove_accents(text: str) -> str:
    if not text: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

def _limpiar_str(s: str) -> str:
    """Corrige encoding, quita espacios dobles pero conserva minúsculas/acentos corregidos."""
    text = str(s).strip().lower()
    for corrupto, corregido in MAPA_CORRECCION.items():
        text = text.replace(corrupto, corregido)
    return _RE_ESPACIOS.sub(" ", text)
 
 
def normalizar_cadena(raw: str) -> str | None:
    """
    Devuelve el nombre canónico de la cadena o None si no está permitida.
    """
    key = _limpiar_str(raw)
    return CADENAS_PERMITIDAS.get(key)
 
 
def simplificar_nombre(nombre: str) -> str:
    """
    Normaliza el nombre quitando acentos para facilitar el matching.
    """
    s = _limpiar_str(nombre)
    s = remove_accents(s)
    s = _RE_EXTRA.sub("", s)
    palabras = [p for p in s.split() if len(p) > 1]
    return " ".join(palabras)
 
 
# ---------------------------------------------------------------------------
# Carga y validación del CSV
# ---------------------------------------------------------------------------
 
def cargar_csv(ruta: Path) -> pd.DataFrame:
    """Carga el CSV y valida que tenga las columnas mínimas."""
    log.info("Cargando %s", ruta)
    df = pd.read_csv(ruta, dtype=str, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
 
    # Renombrar al nombre interno (soporta minúsculas del CSV real y mayúsculas del formato original)
    df = df.rename(columns={k: v for k, v in COLUMNAS_MAP.items() if k in df.columns})
 
    faltantes = COLUMNAS_REQUERIDAS - set(df.columns)
    if faltantes:
        raise ValueError(f"Columnas faltantes en {ruta.name}: {faltantes}")
 
    log.info("  %d filas cargadas", len(df))
    return df
 
 
# ---------------------------------------------------------------------------
# Pipeline de limpieza
# ---------------------------------------------------------------------------
 
def limpiar(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica todas las transformaciones y devuelve el DataFrame listo para Mongo.
    """
    df = df.copy()
 
    # 1. Filtrar por cadenas permitidas
    df["cadena_norm"] = df["Cadena"].apply(normalizar_cadena)
    antes = len(df)
    df = df[df["cadena_norm"].notna()].copy()
    log.info("  Cadenas: %d → %d filas (descartadas %d)", antes, len(df), antes - len(df))
 
    # 2. Limpiar precios
    df["Precio"] = pd.to_numeric(df["Precio"], errors="coerce")
 
    # 2a. Quitar nulos y negativos
    antes = len(df)
    df = df[df["Precio"].notna() & (df["Precio"] > 0)].copy()
    log.info("  Precios inválidos descartados: %d filas", antes - len(df))
 
    # 2b. Outliers por IQR × k
    q1 = df["Precio"].quantile(0.25)
    q3 = df["Precio"].quantile(0.75)
    iqr = q3 - q1
    limite_inf = q1 - IQR_K * iqr
    limite_sup = q3 + IQR_K * iqr
    antes = len(df)
    df = df[df["Precio"].between(limite_inf, limite_sup)].copy()
    log.info(
        "  Outliers de precio eliminados: %d filas "
        "(rango válido: $%.2f – $%.2f)",
        antes - len(df), max(0, limite_inf), limite_sup,
    )
 
    # 3. Coordenadas
    df["LATITUD"]  = pd.to_numeric(df["LATITUD"],  errors="coerce")
    df["LONGITUD"] = pd.to_numeric(df["LONGITUD"], errors="coerce")
    antes = len(df)
    df = df[df["LATITUD"].notna() & df["LONGITUD"].notna()].copy()
    log.info("  Coordenadas inválidas: %d filas descartadas", antes - len(df))
 
    # 4. Limpiar columnas originales para visualización (Producto, Marca, Presentación)
    for col_name in ["Producto", "marca", "presentacion"]:
        if col_name in df.columns:
            df[col_name] = df[col_name].fillna("").apply(_limpiar_str)

    # 5. Nombre simplificado para Gemini (Combina Producto, Presentación y Marca)
    # Ya están limpios por el paso anterior
    df["nombre_simplificado"] = (
        df["Producto"] + " " + 
        (df["presentacion"] if "presentacion" in df.columns else "") + " " + 
        (df["marca"] if "marca" in df.columns else "")
    ).apply(simplificar_nombre)
 
    # 6. Descarte de columnas de ruido
    cols_a_eliminar = [c for c in COLUMNAS_DESCARTADAS if c in df.columns]
    df = df.drop(columns=cols_a_eliminar)
    if cols_a_eliminar:
        log.info("  Columnas descartadas: %s", cols_a_eliminar)
 
    # 7. Renombrar para consistencia de documento
    df = df.rename(columns={
        "Producto": "producto",
        "Precio":   "precio",
        "LATITUD":  "latitud",
        "LONGITUD": "longitud",
    })
    df["cadena"] = df["cadena_norm"]
    df = df.drop(columns=["cadena_norm", "Cadena"]) # Quitamos Cadena (original) y la temporal
 
    # 8. Convertir todas las columnas de texto a minúsculas
    cols_texto = ["cadena", "producto", "nombre_simplificado", "marca", "presentacion", "direccion"]
    for c in cols_texto:
        if c in df.columns:
            df[c] = df[c].astype(str).str.lower().str.strip()
 
    # 9. Deduplicación por Sucursal (Dirección) + Producto
    # Si hay fecha_registro, ordenamos por ella para quedarnos con el último registro visto
    antes = len(df)
    if "fecha_registro" in df.columns:
        # Asegurar formato fecha para sort correcto
        df["fecha_registro_dt"] = pd.to_datetime(df["fecha_registro"], errors="coerce")
        df = df.sort_values("fecha_registro_dt", ascending=True)
        df = df.drop(columns=["fecha_registro_dt"])
    
    # La llave de unicidad es la dirección física de la sucursal + el nombre del producto
    df = df.drop_duplicates(subset=["direccion", "producto"], keep="last")
    log.info("  Deduplicación por sucursal: %d → %d filas (eliminados %d)", antes, len(df), antes - len(df))

    log.info("  Pipeline completado: %d documentos listos", len(df))
    return df
 
 
# ---------------------------------------------------------------------------
# Conversión a documentos MongoDB
# ---------------------------------------------------------------------------
 
def a_documentos(df: pd.DataFrame) -> list[dict[str, Any]]:
    """
    Convierte cada fila en un dict con objeto GeoJSON `location`.
 
    Estructura del documento:
    {
        "cadena":             "Walmart",
        "producto":           "LECHE PASTEURIZADA LALA 1L",
        "nombre_simplificado":"leche pasteurizada",
        "precio":             22.50,
        "location": {
            "type":        "Point",
            "coordinates": [-99.1332, 19.4326]   # [longitud, latitud]
        },
        ...   # resto de columnas del CSV
    }
    """
    docs = []
    for row in df.to_dict(orient="records"):
        lat = row.pop("latitud")
        lon = row.pop("longitud")
        row["location"] = {
            "type": "Point",
            "coordinates": [lon, lat],   # GeoJSON: [long, lat]
        }
        # Precio a float nativo (no numpy)
        row["precio"] = float(row["precio"])
        docs.append(row)
    return docs
 
 
# ---------------------------------------------------------------------------
# Carga a MongoDB
# ---------------------------------------------------------------------------
 
def conectar_mongo(uri: str, db_name: str, col_name: str) -> Collection:
    """Conecta a MongoDB y garantiza el índice 2dsphere."""
    client = MongoClient(uri, serverSelectionTimeoutMS=5_000)
    # Verificar conexión
    client.admin.command("ping")
    col = client[db_name][col_name]
    
    # ── Manejo de índices ──────────────────────────────────────────────────
    col.create_index([("location", GEOSPHERE)], name="idx_location_2dsphere")
    # Índice para acelerar los upserts masivos enormemente
    col.create_index([("location.coordinates", 1), ("producto", 1)], name="idx_upsert_fast")
    
    # Resolver conflicto de índices de texto (MongoDB solo permite uno por colección)
    try:
        # Intentamos borrar el índice antiguo que causa conflicto
        col.drop_index("idx_text_producto")
        log.info("Índice antiguo 'idx_text_producto' eliminado.")
    except Exception:
        pass # Si no existe, no pasa nada
        
    # Índice de texto para búsquedas flexibles (ignora orden de palabras, soporta búsqueda por términos)
    # Lo configuramos explícitamente en español para mejor stemming
    col.create_index(
        [("nombre_simplificado", "text")], 
        name="idx_nombre_texto",
        default_language="spanish"
    )
    
    log.info("Conectado a MongoDB y creados los índices: %s / %s / %s", uri, db_name, col_name)
    return col
 
 
def insertar(col: Collection, docs: list[dict], batch_size: int = BATCH_SIZE) -> int:
    """Inserta o actualiza en lotes para evitar duplicados (Upsert)."""
    total = 0
    for i in range(0, len(docs), batch_size):
        lote = docs[i : i + batch_size]
        
        # Upsert: Si el producto ya existe en esa coordenada, lo actualiza (se queda con el más reciente)
        operaciones = [
            UpdateOne(
                {
                    "location.coordinates": doc["location"]["coordinates"],
                    "producto": doc["producto"]
                },
                {"$set": doc},
                upsert=True
            )
            for doc in lote
        ]
        
        result = col.bulk_write(operaciones, ordered=False)
        # Contamos tanto los insertados nuevos como los actualizados
        procesados = result.upserted_count + result.modified_count
        total += procesados
        log.info("  Lote procesado: %d documentos (total actualizados/insertados: %d)", len(lote), total)
    return total
 
 
# ---------------------------------------------------------------------------
# Orquestador principal
# ---------------------------------------------------------------------------
 
def procesar_archivo(
    ruta: Path,
    col: Collection,
) -> int:
    """Carga, limpia e inserta un archivo CSV. Retorna documentos insertados."""
    df   = cargar_csv(ruta)
    df   = limpiar(df)
    docs = a_documentos(df)
    n    = insertar(col, docs)
    log.info("✔ %s: %d documentos insertados", ruta.name, n)
    return n
 
 
# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
 
def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Pipeline de limpieza y carga de precios a MongoDB."
    )
    p.add_argument(
        "archivos",
        nargs="*",
        type=Path,
        help="Archivos CSV a procesar. Si se omite, se usan todos los CSV de la carpeta 'Datos'.",
    )
    p.add_argument("--mongo-uri", default=MONGO_URI_DEFAULT, help="URI de MongoDB")
    p.add_argument("--db",        default=MONGO_DB_DEFAULT,  help="Base de datos")
    p.add_argument("--coleccion", default=MONGO_COL_DEFAULT, help="Colección")
    p.add_argument(
        "--batch-size",
        type=int,
        default=BATCH_SIZE,
        help="Documentos por insert_many (default: 1000)",
    )
    p.add_argument(
        "--no-mongo",
        action="store_true",
        help="Ejecuta el pipeline sin insertar en MongoDB (modo dry-run / debug)",
    )
    return p
 
 
def main_cli() -> None:
    parser = _build_parser()
    args   = parser.parse_args()
 
    # Resolver lista de archivos
    base_dir = Path(__file__).resolve().parent.parent
    datos_dir = base_dir / "Datos"
    archivos: list[Path] = args.archivos or sorted(datos_dir.glob("*.csv"))
    if not archivos:
        log.error(f"No se encontraron archivos CSV en la carpeta '{datos_dir}'.")
        sys.exit(1)
 
    # Conectar a MongoDB (o modo dry-run)
    col = None
    if not args.no_mongo:
        try:
            col = conectar_mongo(args.mongo_uri, args.db, args.coleccion)
            # Borrar todos los documentos antes de la nueva carga para evitar saturación
            log.info("Limpiando la base de datos antigua...")
            borrados = col.delete_many({})
            log.info("✔ %d documentos antiguos eliminados.", borrados.deleted_count)
        except Exception as exc:
            log.error("No se pudo conectar a MongoDB: %s", exc)
            log.error("Usa --no-mongo para ejecutar en modo dry-run.")
            sys.exit(1)
 
    # Procesar archivos
    total_insertados = 0
    for ruta in archivos:
        if not ruta.exists():
            log.warning("Archivo no encontrado, omitido: %s", ruta)
            continue
        try:
            df   = cargar_csv(ruta)
            df   = limpiar(df)
            docs = a_documentos(df)
 
            if col is not None:
                total_insertados += insertar(col, docs, args.batch_size)
            else:
                log.info("  [dry-run] %d documentos generados (no insertados)", len(docs))
                # Muestra el primer documento como ejemplo
                if docs:
                    import json
                    log.info("  Ejemplo de documento:\n%s", json.dumps(docs[0], ensure_ascii=False, indent=2, default=str))
 
        except Exception as exc:
            log.error("Error procesando %s: %s", ruta, exc)
 
    if col is not None:
        log.info("═══════════════════════════════════════")
        log.info("Total documentos insertados: %d", total_insertados)
 
 
if __name__ == "__main__":
    main_cli()