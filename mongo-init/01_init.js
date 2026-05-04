// mongo-init/01_init.js
// Se ejecuta UNA sola vez cuando el contenedor se crea por primera vez.
// Crea la base de datos, el usuario de la aplicación, la colección
// y los índices que el pipeline necesita.

// ── 1. Autenticarse como root ─────────────────────────────────────────────
db = db.getSiblingDB("admin");

// ── 2. Crear usuario de aplicación con permisos solo sobre precios_db ─────
db.createUser({
  user: "pipeline_user",
  pwd:  "pipeline1234",          // ← cambia en producción
  roles: [
    { role: "readWrite", db: "precios_db" }
  ]
});

// ── 3. Cambiar a la base de datos de la app ───────────────────────────────
db = db.getSiblingDB("precios_db");

// ── 4. Crear la colección con validación de esquema ───────────────────────
db.createCollection("precios", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["cadena", "producto", "precio", "location", "nombre_simplificado"],
      properties: {
        cadena: {
          bsonType: "string",
          description: "Nombre canónico de la cadena (Walmart, Soriana, Chedraui, La Comer)"
        },
        cadena_raw: {
          bsonType: "string",
          description: "Nombre original del CSV"
        },
        producto: {
          bsonType: "string",
          description: "Nombre completo del producto"
        },
        nombre_simplificado: {
          bsonType: "string",
          description: "Nombre reducido para matching con Gemini"
        },
        precio: {
          bsonType: "double",
          minimum: 0,
          description: "Precio en MXN, debe ser positivo"
        },
        location: {
          bsonType: "object",
          required: ["type", "coordinates"],
          properties: {
            type: {
              bsonType: "string",
              enum: ["Point"]
            },
            coordinates: {
              bsonType: "array",
              minItems: 2,
              maxItems: 2,
              description: "[longitud, latitud]"
            }
          }
        }
      }
    }
  },
  validationLevel: "moderate",   // permite documentos existentes aunque fallen
  validationAction: "warn"       // advierte pero no rechaza (útil en desarrollo)
});

// ── 5. Índices ────────────────────────────────────────────────────────────

// Índice geoespacial — requerido por $geoNear / filtro de 10 km
db.precios.createIndex(
  { location: "2dsphere" },
  { name: "idx_location_2dsphere" }
);

// Índice compuesto para las consultas más frecuentes de la app:
//   "dame los precios de X producto en un radio de 10 km"
db.precios.createIndex(
  { nombre_simplificado: 1, cadena: 1, precio: 1 },
  { name: "idx_producto_cadena_precio" }
);

// Índice de texto para búsqueda por nombre de producto (fallback sin Gemini)
db.precios.createIndex(
  { producto: "text", nombre_simplificado: "text" },
  { name: "idx_text_producto", default_language: "spanish" }
);

print("✔ precios_db inicializada correctamente");
print("  · Colección: precios");
print("  · Índices:   2dsphere | producto_cadena_precio | text");
print("  · Usuario:   pipeline_user / precios_db");
