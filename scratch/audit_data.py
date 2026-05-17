from dotenv import load_dotenv
load_dotenv()
import os, re
from pymongo import MongoClient

client = MongoClient(os.getenv("MONGO_URI"), serverSelectionTimeoutMS=10000)
col = client[os.getenv("MONGO_DB_NAME", "precios_db")]["precios"]

# 1. Simulacion de busquedas del usuario
busquedas = ["leche", "crema", "atun", "mango", "manzana", "sandia"]
print("=== SIMULACIÓN DE BÚSQUEDAS ===")
for term in busquedas:
    regex_pattern = f"(?=.*{re.escape(term)}).*"
    results = list(col.find(
        {"nombre_simplificado": {"$regex": regex_pattern, "$options": "i"}},
        {"nombre_simplificado": 1, "producto": 1, "precio": 1, "_id": 0}
    ).sort("precio", 1).limit(5))
    print(f"\n'{term}' -> {len(results)} resultados:")
    for r in results:
        print(f"  - {r.get('nombre_simplificado','?')} (${r.get('precio','?')})")

# 2. Nombres muy cortos (probablemente datos vacíos mal guardados)
print("\n=== NOMBRE_SIMPLIFICADO MUY CORTO (< 5 chars) ===")
count = 0
for d in col.find(
    {"nombre_simplificado": {"$regex": "^.{0,4}$"}},
    {"nombre_simplificado": 1, "producto": 1, "_id": 0}
).limit(10):
    print(repr(d))
    count += 1
print("Total:", count if count < 10 else "10+")

# 3. Campos vacíos críticos
print("\n=== CAMPOS VACÍOS / FALTANTES ===")
print("Sin nombre_simplificado vacío:", col.count_documents({"nombre_simplificado": ""}))
print("Sin producto vacío:           ", col.count_documents({"producto": ""}))
print("Sin location:                 ", col.count_documents({"location": {"$exists": False}}))

# 4. Productos con caracteres raros aún en nombre_simplificado
print("\n=== CARACTERES RAROS EN nombre_simplificado ===")
weird = re.compile(r"[^\w\s\-.]")
count = 0
for d in col.find({}, {"nombre_simplificado": 1, "_id": 0}):
    ns = d.get("nombre_simplificado", "")
    if weird.search(ns):
        print(repr(ns))
        count += 1
        if count >= 15:
            print("...y más")
            break
if count == 0:
    print("Ninguno ✅")

# 5. Precios extremadamente bajos o altos que podrían ser errores de datos
print("\n=== PRECIOS SOSPECHOSOS ===")
print("Precio < 1:", col.count_documents({"precio": {"$lt": 1}}))
print("Precio > 5000:", col.count_documents({"precio": {"$gt": 5000}}))
for d in col.find({"precio": {"$gt": 5000}}, {"nombre_simplificado":1,"precio":1,"_id":0}).limit(5):
    print(f"  ${d['precio']} -> {d.get('nombre_simplificado')}")

# 6. Categoría de productos que pueden generar falsos positivos con el nuevo regex simple
# ej: buscar "leche" pero encontrar "chocolate con leche" -> eso ES correcto
# pero buscar "crema" y encontrar "crema dental" -> eso es un falso positivo
print("\n=== POSIBLES FALSOS POSITIVOS PARA 'crema' ===")
results = list(col.find(
    {"nombre_simplificado": {"$regex": "(?=.*crema).*", "$options": "i"}},
    {"nombre_simplificado": 1, "producto": 1, "_id": 0}
).limit(10))
for r in results:
    print(f"  - {r.get('nombre_simplificado','?')} | {r.get('producto','?')}")

print("\n=== POSIBLES FALSOS POSITIVOS PARA 'sal' ===")
results = list(col.find(
    {"nombre_simplificado": {"$regex": "(?=.*\\bsal\\b).*", "$options": "i"}},
    {"nombre_simplificado": 1, "producto": 1, "_id": 0}
).limit(10))
for r in results:
    print(f"  - {r.get('nombre_simplificado','?')}")
