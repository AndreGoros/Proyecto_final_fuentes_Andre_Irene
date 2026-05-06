# Sistema de Optimización de Canasta Básica (PROFECO + AI)

Este proyecto es una solución tecnológica diseñada para ayudar a los usuarios a encontrar el costo total más bajo para su lista de compras. El sistema integra datos oficiales de la PROFECO, Inteligencia Artificial Generativa (Gemini) y procesamiento geoespacial para ofrecer un cálculo de ahorro real que incluye el costo de traslado (gasolina).

---

## 🚀 Estado Actual del Proyecto

Actualmente, el proyecto es **100% funcional de extremo a extremo (End-to-End)**, contando con las siguientes piezas:
1. **Limpieza e Ingesta de Datos (Inteligente):** El sistema procesa CSVs masivos de PROFECO aplicando correcciones automáticas de encoding y combinando producto + presentación + marca para crear un **Índice de Texto** de búsqueda flexible.
2. **Infraestructura:** MongoDB en Docker con índices espaciales (`2dsphere`) y un **Text Index** optimizado para español que permite encontrar productos incluso con ligeros errores de escritura.
3. **API Backend:** Servidor FastAPI con **Cerebro de Corrección (Gemini)**. Antes de buscar en la DB, el sistema usa IA para normalizar typos (ej: "gitomate" -> "jitomate") y extraer cantidades.
4. **Frontend:** Interfaz interactiva (Dark Mode) con desglose detallado, incluyendo distancias reales y cálculo de gasolina.
5. **CI/CD y Testing:** Pipeline automatizado con GitHub Actions y pruebas unitarias con `Pytest`.

---

## 🛠️ Stack Tecnológico y Herramientas

Este proyecto hace uso de tecnologías modernas para asegurar rendimiento, escalabilidad y una experiencia de usuario fluida.

### Backend y Core Logic
* **FastAPI**: Framework web moderno y de alto rendimiento para construir APIs con Python, basado en validación de tipos. Ideal para manejar peticiones asíncronas.
* **Python 3**: Lenguaje principal del proyecto.
* **Pydantic**: Validación de datos y gestión de esquemas, asegurando que los *payloads* de la API sean estrictamente correctos.

### Base de Datos y Procesamiento Geoespacial
* **MongoDB**: Base de datos NoSQL elegida por su flexibilidad con documentos y sus excelentes capacidades nativas para índices geoespaciales (`2dsphere`).
* **Motor**: Driver oficial asíncrono de MongoDB para Python, que maximiza el throughput del servidor FastAPI.
* **Pandas**: Utilizado en el pipeline ETL para ingestar, limpiar, transformar y procesar eficientemente los pesados archivos CSV de PROFECO.

### Inteligencia Artificial
* **Google Gemini (Vision)**: Integrado para el análisis inteligente de fotografías de listas de compras. Realiza OCR y extracción estructurada de datos, infiriendo productos, marcas y gramajes mediante prompting avanzado.

### Frontend (UI/UX)
* **HTML5, CSS3 y Vanilla JavaScript**: Aplicación web ligera construida sin frameworks complejos, garantizando tiempos de carga rápidos y un rendimiento fluido.
* **Diseño Premium**: Interfaz moderna aplicando tendencias de diseño como *Glassmorphism*, transiciones suaves y modo oscuro (*Dark Mode*) nativo.

### DevOps, Pruebas e Infraestructura
* **Docker & Docker Compose**: Contenerización de la base de datos (y su panel Mongo-Express) para garantizar un entorno determinista de desarrollo.
* **GitHub Actions**: Pipeline de Integración Continua (CI) que valida la integridad del código y ejecuta las pruebas automáticas.
* **Pytest**: Framework utilizado para diseñar pruebas unitarias automatizadas que protegen la lógica de los endpoints y los scripts de limpieza.
* **Ngrok**: Túnel reverso automatizado en el proyecto para poder exponer el servidor local a internet y probar la aplicación en dispositivos móviles fácilmente.

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
  ┣ 📂 scratch/               # 🧪 Laboratorio: Scripts de prueba y validación
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
* **`services/query_service.py`**: **El núcleo matemático**. Incluye un *parser* de lenguaje natural para extraer cantidades (unidades, kg, litros). Ejecuta la agregación geoespacial `$geoNear` en MongoDB y filtra productos asegurando que los precios pertenezcan a la sucursal exacta, calculando el ahorro real incluyendo el traslado.
* **`requirements.txt`**: Librerías y dependencias exclusivas para correr la API.

### 2. `data_pipeline/` (Limpieza de Datos PROFECO)
Contiene los scripts locales que transforman el catálogo crudo en datos geolocalizables.
* **`limpieza.py`**: Limpia los CSV filtrando 4 corporativos objetivo. **Sanea la corrupción de encoding** mediante un mapa exhaustivo (ej: `pi¥a` → `piña`, `Jamàn` → `jamón`, `Clµsico` → `clásico`), normaliza texto y limpia las columnas originales para que el frontend muestre nombres legibles y con acentos correctos.
* **`pipeline_limpieza.py`**: Interfaz de terminal (CLI) para correr el pipeline cómodamente (se puede ejecutar directamente desde la raíz del proyecto).
* **`requirements.txt`**: Dependencias analíticas (Pandas, PyMongo) exclusivas para procesar datos.
 
### 3. `scratch/` (Laboratorio y Pruebas Rápidas)
Carpeta utilizada para validar algoritmos de forma aislada antes de integrarlos al flujo principal.
* **`check_data.py`**: Verifica la corrección de encoding y limpieza en DB.
* **`check_db_items.py`**: Búsqueda manual de productos para depurar el catálogo.
* **`check_mongo_geo.py`**: Valida que los índices `$geoNear` funcionen correctamente.
* **`check_store.py`**: Lista el inventario completo de una sucursal específica.
* **`count.py`**: Conteo rápido de documentos cargados por colección.
* **`inspect_atun.py`**: Valida la corrección del error "Atén" -> "atun".
* **`inspect_db.py`**: Muestra ejemplos aleatorios de documentos para inspección de esquema.
* **`list_gemini_models.py`**: Consulta modelos disponibles en la API Key de Google.
* **`test_clean_names.py`**: Valida la eliminación de ruidos y distractores en nombres.
* **`test_full_logic.py`**: Prueba el flujo completo (IA -> Parser -> Búsqueda) con mocks.
* **`test_full_regex.py`**: Valida patrones de búsqueda complejos y negativos.
* **`test_gemini_api.py`**: Diagnóstico básico de conexión con Google Gemini.
* **`test_gemini_api_v3.py`**: Prueba de cuotas y rendimiento del modelo Flash.
* **`test_gemini_correction.py`**: Prueba aislada de la IA corrigiendo ortografía.
* **`test_new_logic.py`**: Borrador de la lógica de tiendas completas/incompletas.
* **`test_parser.py`**: Valida la extracción de cantidades (1kg, 2lt, etc).
* **`test_phonetic_regex.py`**: Desarrollo de reglas de ortografía flexible (g/j, s/z).
* **`test_phonetic_regex_fixed.py`**: Versión final corregida de la búsqueda fonética.
* **`test_real_db.py`**: Simulación de búsqueda real contra los datos de PROFECO.
* **`test_real_search.py`**: Validación de resultados por cercanía y disponibilidad real.
* **`inspect_quesos.py`**: Diagnóstico de variedades de queso (Manchego, Oaxaca, Chihuahua) en el catálogo.
* **`debug_missing.py`**: Herramienta de autopsia para investigar por qué productos básicos (ej. Jamón) no aparecen en búsquedas.
* **`find_real_bread.py`**: Localiza nombres técnicos de panificados (ej. "Pan de caja" vs "Pan blanco").
* **`test_missing_items.py`**: Simulación de estrés para productos específicos que el usuario reporta como no encontrados.

### 4. Infraestructura Docker & MongoDB
* **`docker-compose.yml`** (En la raíz): Orquestador de contenedores que levanta el servidor de MongoDB y Mongo-Express (Interfaz Gráfica para la DB).
* **`mongo-init/01_init.js`**: Script de arranque de MongoDB. Se ejecuta *automáticamente* la primera vez que inicia la base de datos para crear los usuarios de seguridad, validar el formato de los datos insertados y crear el índice `2dsphere` para que funcionen las búsquedas por distancia.

### 5. Carpetas y Archivos Generales
* **`Datos/`**: Carpeta dedicada a almacenar temporalmente los pesados archivos `.csv` descargados directamente del sitio de PROFECO.
* **`frontend/`**: Directorio estratégicamente preparado (y por ahora vacío) para alojar el código futuro de la interfaz web gráfica.
* **`start.py`**: Orquestador principal de desarrollo. Con un solo comando (`python start.py`) levanta tu servidor FastAPI en segundo plano y además abre automáticamente un túnel web con **ngrok** para compartir tu app en internet.
* **`.env.example`**: Plantilla unificada de variables de entorno que incluye credenciales de base de datos y llaves para la Inteligencia Artificial.

---

## 📊 Estructura del Dataset (PROFECO)

El sistema procesa e indexa las siguientes 10 columnas clave para garantizar precisión y ahorro:

| Columna | Descripción | Uso en el Sistema |
| :--- | :--- | :--- |
| **`producto`** | Nombre base del artículo | Identificación primaria. |
| **`presentacion`** | Gramaje o medida (ej: 1 Kg, 900ml) | Diferenciación de precios unitarios. |
| **`marca`** | Fabricante (ej: Lala, Alpura) | Búsqueda específica solicitada por el usuario. |
| **`categoria`** | Clasificación oficial | Organización y filtrado. |
| **`precio`** | Costo monetario | Base del cálculo de ahorro. |
| **`fecha_registro`** | Timestamp de captura | Validación de vigencia del precio. |
| **`cadena_comercial`**| Nombre de la corporación | Agrupación por tienda (Walmart, Chedraui, etc). |
| **`direccion`** | Ubicación textual | Visualización en los resultados del frontend. |
| **`latitud / longitud`**| Coordenadas físicas | Cálculo de distancia y costo de gasolina ($geoNear). |
| **`nombre_simplificado`**| Producto + Marca + Presentación | **Columna calculada** para el Índice de Texto (Fuzzy Search). |

> [!NOTE]
> Durante la limpieza, el sistema aplica un filtro de **Outliers (IQR_K=10.0)** para eliminar errores de captura en el CSV original, pero protegiendo productos naturalmente caros como cortes de carne o paquetes familiares.

---

## 🧠 Motor de Búsqueda Inteligente (Fuzzy Search)

Para lograr que el sistema entienda consultas informales o con errores, implementamos una estrategia de **dos capas**:

### Capa 1: Normalización con IA (Pre-procesamiento)
Antes de tocar la base de datos, la lista del usuario (texto o foto) pasa por **Google Gemini 1.5 Flash**. Esta capa se encarga de:
*   **Corrección Ortográfica:** Convierte "gitomate" en "jitomate".
*   **Detección de Entidades:** Separa la cantidad (6), la unidad (litros), la marca (lala) y el producto (leche).
*   **Estandarización:** Convierte términos informales en nombres que tienen mayor probabilidad de existir en el catálogo oficial.

### Capa 2: Índice de Texto en MongoDB (Recuperación)
Una vez normalizada la consulta, el backend realiza una búsqueda utilizando un **Índice de Texto** configurado en español:
*   **Independencia de Orden:** "leche lala" o "lala leche" devolverán el mismo resultado.
*   **Matching Enriquecido:** Al combinar `producto + marca + presentacion` en una sola columna indexada, el sistema puede encontrar "atun dolores lata" aunque esas palabras vengan de 3 columnas distintas del CSV original.
*   **Filtrado Geoespacial:** Los resultados se limitan en tiempo real a las sucursales dentro del radio de 10km del usuario, ordenando por precio final.
*   **Flexibilidad Fonética:** Implementación de reglas de regex personalizadas para compensar confusiones comunes en español (`g/j`, `s/z/c`, `b/v`, `h` muda y `r/rr`), permitiendo que búsquedas como "arros" o "gitomate" encuentren resultados correctos sin depender exclusivamente de la IA.

### Capa 3: Categorización de Canasta (Optimización)
El sistema divide los resultados en dos categorías para una mejor decisión de compra:
1. **Tiendas Completas:** Aquellas que tienen el 100% de los productos solicitados (priorizadas por ahorro).
2. **Tiendas Incompletas:** Aquellas donde faltan uno o más artículos, marcando claramente qué productos no están disponibles y resaltando el ahorro parcial.


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
> [!TIP]
> **Precisión en la búsqueda:** El sistema busca siempre la opción más económica. Para productos que puedan confundirse con frutas (ej: "miel" puede coincidir con "piña miel"), se recomienda ser específico escribiendo **"miel de abeja"**.
---

## 💡 Ejemplos de Uso

El sistema es capaz de procesar lenguaje natural tanto en texto como en fotos gracias a su **Capa de Corrección con Gemini**. Aquí algunos ejemplos:

*   **Búsquedas con Marca:** "leche lala entera", "atun dolores en aceite".
*   **Cantidades y Unidades:** "6 litros leche alpura", "3 kg jitomate", "2 latas de atun".
*   **Flexibilidad (Typos):** "6 latas atun, gitomate, 2 chocorole" (El sistema corregirá "gitomate" a "jitomate" y encontrará los Chocorroles).
*   **Búsquedas Genéricas:** "huevo", "cebolla", "arroz". (Busca automáticamente la opción más económica de la sucursal).

**Tip:** Si usas la cámara, asegúrate de que la marca y el tamaño sean visibles; la IA de Gemini extraerá los detalles para que la comparativa sea justa entre tiendas.

---

## 🧪 Guía de Scripts de Validación (Laboratorio)

La carpeta `scratch/` contiene utilidades para mantenimiento y pruebas profundas:

*   **Integridad de Datos:**
    *   `count.py`: Conteo rápido de documentos por colección.
    *   `inspect_db.py`: Visualización de esquemas y estructuras de datos.
    *   `check_data.py`: Verifica la limpieza de nombres y corrección de encoding.
    *   `inspect_atun.py`: Script específico para validar el caso de éxito de "Atén" vs "atun".

*   **Pruebas de Motor de Búsqueda:**
    *   `test_parser.py`: Valida el extractor de cantidades y unidades (kg, lt, latas).
    *   `test_phonetic_regex_fixed.py`: Valida las reglas de ortografía flexible (g/j, s/z/c, etc.).
    *   `test_clean_names.py`: Prueba la eliminación de ruido y distractores en los nombres.
    *   `test_full_logic.py`: Simulación integral (Corrección -> Parser -> Regex) sin tocar la DB.

*   **Validación con Base de Datos Real:**
    *   `check_mongo_geo.py`: Prueba de conectividad e índices geoespaciales (`$geoNear`).
    *   `test_real_db.py`: Búsquedas masivas contra el dataset real de PROFECO.
    *   `test_real_search.py`: Simulación de búsqueda completa basada en ubicación y cercanía.
    *   `check_store.py`: Inspección detallada del inventario de una tienda específica.

*   **Diagnóstico de IA (Gemini):**
    *   `list_gemini_models.py`: Lista los modelos disponibles para tu API Key (ej. v1.5 vs v2.0).
    *   `test_gemini_api_v3.py`: Prueba de conectividad, cuota y latencia de la API de Google.
    *   `test_gemini_correction.py`: Valida específicamente el prompt de corrección ortográfica.

