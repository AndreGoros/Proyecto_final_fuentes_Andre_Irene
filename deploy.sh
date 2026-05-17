#!/bin/bash
# ══════════════════════════════════════════════════════════
#  deploy.sh — Despliega la app a Google Cloud Run
#  Uso: bash deploy.sh
#  Requisitos: gcloud CLI instalado y autenticado
# ══════════════════════════════════════════════════════════

set -e  # Detener si cualquier comando falla

# ── Configuración — EDITA ESTOS VALORES ───────────────────
PROJECT_ID="tu-proyecto-gcloud"          # gcloud projects list
REGION="us-central1"
SERVICE_NAME="canasta-basica-api"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Variables de entorno para Cloud Run (NO pongas valores aquí,
# usa Secret Manager en producción real)
MONGO_URI="mongodb+srv://usuario:password@cluster.mongodb.net/profeco?retryWrites=true&w=majority"
GEMINI_API_KEY="tu_gemini_api_key"
MONGO_DB_NAME="profeco"
ALLOWED_ORIGINS="*"
# ──────────────────────────────────────────────────────────

echo "🚀 Iniciando despliegue a Cloud Run..."
echo "   Proyecto : $PROJECT_ID"
echo "   Región   : $REGION"
echo "   Servicio : $SERVICE_NAME"
echo ""

# 1. Autenticar con Google Cloud
echo "🔑 Verificando autenticación..."
gcloud auth configure-docker --quiet

# 2. Establecer proyecto activo
gcloud config set project $PROJECT_ID

# 3. Habilitar APIs necesarias (solo la primera vez)
echo "⚙️  Habilitando APIs de Google Cloud..."
gcloud services enable \
    run.googleapis.com \
    containerregistry.googleapis.com \
    secretmanager.googleapis.com \
    --quiet

# 4. Build y push de la imagen Docker
echo "🐳 Construyendo imagen Docker..."
docker build -t $IMAGE_NAME .

echo "📤 Subiendo imagen al registro..."
docker push $IMAGE_NAME

# 5. Desplegar en Cloud Run
echo "☁️  Desplegando en Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --concurrency 80 \
    --timeout 60 \
    --set-env-vars "MONGO_URI=${MONGO_URI}" \
    --set-env-vars "GEMINI_API_KEY=${GEMINI_API_KEY}" \
    --set-env-vars "MONGO_DB_NAME=${MONGO_DB_NAME}" \
    --set-env-vars "ALLOWED_ORIGINS=${ALLOWED_ORIGINS}" \
    --set-env-vars "ENVIRONMENT=production" \
    --quiet

# 6. Obtener URL del servicio
echo ""
echo "✅ ¡Despliegue exitoso!"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region $REGION \
    --format "value(status.url)")
echo "🌐 URL del servicio: $SERVICE_URL"
echo ""
echo "📝 Próximo paso: actualiza la URL en frontend/app.js"
echo "   Reemplaza la URL de ngrok/localhost por: $SERVICE_URL"
