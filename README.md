# Sistema de Optimización de Canasta Básica (PROFECO + AI)

Este proyecto es una solución tecnológica diseñada para ayudar a los usuarios a encontrar el costo total más bajo para su lista de compras. El sistema integra datos oficiales de la PROFECO, Inteligencia Artificial Generativa (Gemini) y procesamiento geoespacial para ofrecer un cálculo de ahorro real que incluye el costo de traslado (gasolina).

---

## 🚀 Estado Actual del Proyecto

Actualmente, el proyecto es **100% funcional de extremo a extremo (End-to-End)**, contando con las siguientes piezas:
1. **Limpieza e Ingesta de Datos (Completada y Optimizada):** El sistema es capaz de recibir CSVs masivos de PROFECO. Utiliza un algoritmo de "Upsert" y un índice compuesto en MongoDB para cargar grandes volúmenes de datos sin duplicar productos, manteniendo automáticamente el precio más reciente.
2. **Infraestructura (Completada):** Se tiene configurado MongoDB en contenedores Docker con índices espaciales (`2dsphere`) y de búsqueda.
3. **API Backend (Completada):** Servidor asíncrono robusto (FastAPI) que evalúa las **15 sucursales físicas más cercanas** para encontrar la mejor combinación, retornando tanto los productos hallados como un reporte de artículos faltantes en cada sucursal.
4. **Frontend (Completado):** Interfaz gráfica interactiva (Dark Mode & Glassmorphism) que permite al usuario subir su lista, pedir su ubicación GPS y visualizar tarjetas con distancias, costos de gasolina y alertas de productos no encontrados.
5. **CI/CD y Testing (Integrado):** Se implementó integración continua usando GitHub Actions con validaciones automatizadas de sintaxis y pruebas unitarias usando `Pytest`.

---

## 📂 Organización del Repositorio

El proyecto ha sido rediseñado utilizando arquitectura de microservicios y una estricta separación por responsabilidades.

### 🌳 Árbol de Arquitectura (Niveles)
```text
📦 Proyecto_final_fuentes_Andre_Irene
 ┣ 📂 .github/workflows/     # 🤖 Nivel 5: Integración Continua (CI/CD)
 ┃ ┗ 📜 ci.yml               #   Pipeline automatizado de GitHub Actions
 ┣ 📂 backend/               # 🧠 Nivel 2: Lógica de Negocio y API
 ┃ ┣ 📜 main.py              #   Endpoints principales (FastAPI)
 ┃ ┣ 📜 database.py          #   Conexión asíncrona a MongoDB
 ┃ ┣ 📜 schemas.py           #   Validación estricta de datos (Pydantic)
 ┃ ┣ 📂 services/            #   Lógica pesada
 ┃ ┃ ┣ 📜 gemini_service.py  #     Conexión con IA (Google Gemini Vision)
 ┃ ┃ ┗ 📜 query_service.py   #     Matemáticas, deducción de faltantes y $geoNear
 ┃ ┗ 📜 requirements.txt     #   Dependencias del servidor
 ┣ 📂 frontend/              # 🎨 Nivel 1: Interfaz Gráfica del Usuario (UI)
 ┃ ┣ 📜 index.html           #   Estructura de la aplicación
 ┃ ┣ 📜 styles.css           #   Estilos Premium (Dark Mode & Glassmorphism)
 ┃ ┗ 📜 app.js               #   Lógica de interacción y llamadas a la API
 ┣ 📂 data_pipeline/         # ⚙️ Nivel 3: Ingesta y Limpieza de Datos (ETL)
 ┃ ┣ 📜 limpieza.py          #   Core de limpieza (Upserts sin duplicados)
 ┃ ┣ 📜 pipeline_limpieza.py #   Interfaz de comandos (CLI)
 ┃ ┗ 📜 requirements.txt     #   Dependencias de procesamiento (Pandas, PyMongo)
 ┣ 📂 tests/                 # 🧪 Pruebas Unitarias Automatizadas
 ┃ ┣ 📜 test_api.py          #   Validación del backend y endpoints
 ┃ ┗ 📜 test_limpieza.py     #   Validación del algoritmo de Pandas
 ┣ 📂 mongo-init/            # 🗄️ Nivel 4: Infraestructura de Base de Datos
 ┃ ┗ 📜 01_init.js           #   Inicialización de Mongo e índices 2dsphere
 ┣ 📂 Datos/                 # 📥 Origen de Datos (Aquí van los CSVs de PROFECO)
 ┣ 📜 start.py               # 🚀 Orquestador General (Levanta API + Túnel ngrok)
 ┣ 📜 docker-compose.yml     # 🐳 Definición de contenedores (Mongo + Mongo-Express)
 ┗ 📜 .env.example           # 🔑 Plantilla de credenciales y variables de entorno
```

A continuación se detalla qué hace cada componente:

### 1. `backend/` (El Cerebro de la API)
Contiene el servidor web que coordina las interacciones del usuario, la IA y la base de datos.
* **`main.py`**: Punto de entrada del servidor FastAPI. Expone las rutas HTTP principales como `/api/v1/analizar-foto`.
* **`database.py`**: Define la conexión asíncrona y segura a MongoDB utilizando la librería `motor`.
* **`schemas.py`**: Define los modelos y reglas *Pydantic* para validar estrictamente la información que entra y sale de la API.
* **`services/gemini_service.py`**: Aislador de la API de Google Gemini. Analiza la imagen recibida, extrae los productos y fuerza a la IA a respetar la marca, tamaño y medida exactos.
* **`services/query_service.py`**: **El núcleo matemático**. Ejecuta la agregación geoespacial `$geoNear` en MongoDB, filtra productos asegurando que los precios pertenezcan a **la sucursal exacta más cercana** (evitando cruces de estado) y calcula en tiempo real el costo de gasolina (utilizando parámetros configurables desde `.env`).
* **`requirements.txt`**: Librerías y dependencias exclusivas para correr la API.

### 2. `data_pipeline/` (Limpieza de Datos PROFECO)
Contiene los scripts locales que transforman el catálogo crudo en datos geolocalizables.
* **`limpieza.py`**: Limpia los CSV filtrando 4 corporativos objetivo (Walmart, Soriana, Chedraui, La Comer). Remueve errores, limpia texto preservando semántica y genera coordenadas `GeoJSON Point`.
* **`pipeline_limpieza.py`**: Interfaz de terminal (CLI) para correr el pipeline cómodamente (se puede ejecutar directamente desde la raíz del proyecto).
* **`requirements.txt`**: Dependencias analíticas (Pandas, PyMongo) exclusivas para procesar datos.

### 3. Infraestructura Docker & MongoDB
* **`docker-compose.yml`** (En la raíz): Orquestador de contenedores que levanta el servidor de MongoDB y Mongo-Express (Interfaz Gráfica para la DB).
* **`mongo-init/01_init.js`**: Script de arranque de MongoDB. Se ejecuta *automáticamente* la primera vez que inicia la base de datos para crear los usuarios de seguridad, validar el formato de los datos insertados y crear el índice `2dsphere` para que funcionen las búsquedas por distancia.

### 4. Carpetas y Archivos Generales
* **`Datos/`**: Carpeta dedicada a almacenar temporalmente los pesados archivos `.csv` descargados directamente del sitio de PROFECO.
* **`frontend/`**: Directorio estratégicamente preparado (y por ahora vacío) para alojar el código futuro de la interfaz web gráfica.
* **`start.py`**: Orquestador principal de desarrollo. Con un solo comando (`python start.py`) levanta tu servidor FastAPI en segundo plano y además abre automáticamente un túnel web con **ngrok** para compartir tu app en internet.
* **`.env.example`**: Plantilla unificada de variables de entorno que incluye credenciales de base de datos y llaves para la Inteligencia Artificial.

---

## 🛠️ Cómo correr el sistema completo (Local-First)

1. **Configura tu entorno:**
   Copia la plantilla de variables de entorno y agrega tu API Key de Gemini:
   ```bash
   cp .env.example .env
   ```

2. **Enciende el motor de Base de Datos:**
   ```bash
   docker-compose up -d
   ```

3. **Carga los datos reales:**
   - Descarga un archivo `.csv` de PROFECO y mételo dentro de la carpeta `Datos/`.
   - Crea un entorno virtual, actívalo y procesa los datos:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     pip install -r data_pipeline/requirements.txt
     python data_pipeline/pipeline_limpieza.py
     ```

4. **Arranca tu Servidor y el Frontend:**
   - En la misma terminal (asegúrate de que el `.venv` siga activado), instala las dependencias del servidor y córrelo:
   ```bash
   pip install -r backend/requirements.txt
   python start.py
   ```
   *(Abre tu navegador en `http://localhost:8000/` para utilizar la interfaz visual. Además, en tu terminal verás una URL pública generada por ngrok con la que puedes usar la aplicación desde tu teléfono)*.