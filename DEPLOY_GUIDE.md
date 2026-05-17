# 🚀 Guía de Deploy: Railway (backend) + Cloudflare Pages (frontend)

## Estructura esperada del repo
```
tu-repo/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── ...
├── frontend/
│   ├── index.html
│   ├── app.js
│   ├── styles.css
│   └── _redirects          ← archivo nuevo
├── Dockerfile.railway      ← archivo nuevo
├── railway.toml            ← archivo nuevo
└── .gitignore
```

---

## PASO 1 — Preparar el repo (5 min)

1. Copia los archivos nuevos a tu repo:
   - `Dockerfile.railway` → raíz
   - `railway.toml` → raíz
   - `_redirects` → dentro de `frontend/`

2. Aplica los parches de código:
   - `health_check_patch.py` → pega en `backend/main.py`
   - `api_url_patch.js` → pega al tope de `frontend/app.js`

3. Asegúrate de que `.gitignore` incluye:
   ```
   .env
   __pycache__/
   *.pyc
   .DS_Store
   ```

4. Commit y push a GitHub.

---

## PASO 2 — Railway: Backend + MongoDB (15 min)

1. Ve a https://railway.app → "Start a New Project"
2. Elige **"Deploy from GitHub repo"** → selecciona tu repo
3. Railway detecta el `railway.toml` automáticamente ✅

### Agregar MongoDB:
4. En tu proyecto Railway → **"+ New"** → **"Database"** → **"MongoDB"**
5. Railway crea el servicio y genera la variable `MONGODB_URL` automáticamente

### Variables de entorno:
6. En tu servicio FastAPI → **"Variables"** → agrega:
   ```
   MONGO_URI          = ${{MongoDB.MONGODB_URL}}   ← referencia automática de Railway
   MONGO_DB_NAME      = profeco
   GEMINI_API_KEY     = tu_clave_aqui
   ALLOWED_ORIGINS    = https://tu-app.pages.dev   ← la llenas después del Paso 3
   ```

7. Deploy automático al guardar. Espera ~2 min.
8. Copia la URL pública: `https://tu-app.up.railway.app`

---

## PASO 3 — Migrar datos a MongoDB de Railway (30-60 min)

Railway te da una MongoDB con conexión pública mientras configuras.

```bash
# 1. Obtén el connection string desde Railway → MongoDB → Variables → MONGODB_URL

# 2. Exportar desde tu Docker local:
docker exec -it $(docker ps -qf name=mongo) mongodump \
  --db profeco \
  --out ./backup_profeco

# 3. Restaurar en Railway MongoDB:
mongorestore \
  --uri "mongodb://mongo:password@containers-us-west-XXX.railway.app:PORT" \
  --db profeco \
  ./backup_profeco/profeco

# Con 1.4M documentos esto tarda ~15-30 min dependiendo de tu internet
```

### Verificar índices después de migrar:
```javascript
// Conéctate con mongosh y verifica:
use profeco
db.productos.getIndexes()
// Debes ver el índice 2dsphere y el text index
// Si no están, créalos:
db.productos.createIndex({ "ubicacion": "2dsphere" })
db.productos.createIndex({ "nombre_simplificado": "text" }, { default_language: "spanish" })
```

---

## PASO 4 — Cloudflare Pages: Frontend (10 min)

1. Ve a https://pages.cloudflare.com → "Create a project"
2. **"Connect to Git"** → selecciona tu repo
3. Configuración de build:
   ```
   Framework preset:     None
   Build command:        (vacío)
   Build output dir:     frontend
   Root directory:       (vacío)
   ```
4. Deploy → Cloudflare te da una URL tipo `https://tu-app.pages.dev`

### Actualizar el proxy en _redirects:
5. Abre `frontend/_redirects` y reemplaza la URL placeholder:
   ```
   /api/*  https://tu-app.up.railway.app/api/:splat  200
   ```
6. Commit + push → Cloudflare re-deploya automáticamente en ~30s

### Actualizar CORS en Railway:
7. Railway → tu servicio → Variables:
   ```
   ALLOWED_ORIGINS = https://tu-app.pages.dev
   ```

---

## PASO 5 — Verificar que todo funciona

```bash
# 1. Health check del backend
curl https://tu-app.up.railway.app/api/health
# Esperado: {"status":"ok","database":"connected"}

# 2. Una query de prueba
curl "https://tu-app.up.railway.app/api/buscar?q=leche"

# 3. Abrir el frontend
# https://tu-app.pages.dev
```

---

## Resumen de costos

| Servicio | Costo | Límite gratis |
|---|---|---|
| Railway (FastAPI) | ~$2-4/mes | $5 créditos/mes |
| Railway (MongoDB) | ~$1-3/mes | incluido en créditos |
| Cloudflare Pages | $0 | ilimitado |
| **Total** | **~$0-7/mes** | según tráfico |

> Con poco tráfico inicial los $5 de Railway suelen cubrir todo.
> Si se acaban: plan Hobby a $20/mes incluye $20 de créditos (más que suficiente).

---

## Dominio personalizado (opcional, gratis)

- Railway: Settings → Networking → Custom Domain
- Cloudflare Pages: Settings → Custom Domains
- Si tienes un dominio en Cloudflare, la integración es de 1 clic.
