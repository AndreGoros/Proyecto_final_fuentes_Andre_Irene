#!/bin/bash
# ══════════════════════════════════════════════════════════
#  migrate_to_atlas.sh — Migra datos de Docker local a Atlas
#  Uso: bash migrate_to_atlas.sh
# ══════════════════════════════════════════════════════════

set -e

# ── Configuración — EDITA ESTOS VALORES ───────────────────
LOCAL_DB="profeco"
ATLAS_URI="mongodb+srv://<usuario>:<password>@<cluster>.mongodb.net"
BACKUP_DIR="./atlas_migration_backup"
# ──────────────────────────────────────────────────────────

echo "📦 Migrando datos a MongoDB Atlas..."

# Opción A: mongodump + mongorestore (recomendado si tienes muchos datos)
echo ""
echo "━━━ OPCIÓN A: mongodump / mongorestore ━━━"
echo "1. Exportar desde Docker local:"
echo "   docker exec -it \$(docker ps -qf name=mongo) mongodump \\"
echo "     --db $LOCAL_DB \\"
echo "     --out /backup"
echo ""
echo "   docker cp \$(docker ps -qf name=mongo):/backup $BACKUP_DIR"
echo ""
echo "2. Restaurar en Atlas:"
echo "   mongorestore \\"
echo "     --uri \"$ATLAS_URI\" \\"
echo "     --db $LOCAL_DB \\"
echo "     $BACKUP_DIR/$LOCAL_DB"

echo ""
echo "━━━ OPCIÓN B: Re-ingestar desde los CSVs (más limpio) ━━━"
echo "Si prefieres regenerar los datos desde cero en Atlas:"
echo ""
echo "1. Actualiza tu .env con la nueva MONGO_URI de Atlas"
echo "2. Corre el pipeline de limpieza normal:"
echo "   python data_pipeline/pipeline_limpieza.py"
echo ""
echo "La ventaja es que te aseguras de que los índices se creen correctamente."

echo ""
echo "━━━ PASO CRÍTICO: Verificar índices en Atlas ━━━"
cat << 'EOF'
Después de migrar, verifica los índices en la consola de Atlas:

En Atlas → Collections → profeco → Indexes, debes ver:

1. Índice geoespacial:
   { "ubicacion": "2dsphere" }

2. Text Index para búsqueda fuzzy:
   { "nombre_simplificado": "text" }
   Con collation: { locale: "es", strength: 2 }

Si no existen, créalos desde mongo-init/01_init.js o con:
   db.productos.createIndex({ "ubicacion": "2dsphere" })
   db.productos.createIndex(
     { "nombre_simplificado": "text" },
     { default_language: "spanish" }
   )
EOF

echo ""
echo "✅ Guía de migración completada."
